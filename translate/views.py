"""
views
"""
import mimetypes
import os
import io
import urllib.parse
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings

from translate.forms import GlossaryForm
from translate.forms import DocumentForm
from translate.forms import TextForm
from translate.models import File
import lib.translator
import lib.glossary
from .consts import STATUS

def index(request):
    """index page"""
    return redirect('translate/translator')

def translate_index(request):
    """index page"""
    return redirect('translate:translator')

def glossary(request):
    """glossary views"""
    lib.glossary.upload_glossary_on_google()
    lib.glossary.create_glossary_on_google()
    default_form_value = {'target_lang':'ja'}

    form = GlossaryForm(initial=default_form_value)

    tbody_html = lib.glossary.create_glossary_list_tbody_html(request, STATUS)

    return render(request,
                  'translate/glossary.html',
                  {'file_list_data': tbody_html,
                   'form': form,
                   'STATUS': STATUS,
                   'nbar': "glossary"},
                 )

# Create your views here.
def translator(request):
    """get list of files"""
    default_form_value = {'target_lang':'ja'}

    form = DocumentForm(initial=default_form_value)

    tbody_html = lib.translator.create_file_list_tbody_html(request, STATUS)

    glossry_tbody_html = lib.glossary.create_glossary_for_trans_tbody_html(request)

    return render(request,
                  'translate/translator.html',
                  {'file_list_data': tbody_html,
                   'glossary_list_data': glossry_tbody_html,
                   'form': form,
                   'STATUS': STATUS,
                   'nbar': "trans"},
                 )

def help_index(request):
    """help page"""
    return render(request,
                  'translate/help.html',
                  {'nbar': "help"},
                 )

def translate_text(request):
    """translate text"""

    default_form_value = {'target_lang':'ja'}
    #Set the session key to POST
    copied_post_data = request.POST.copy()
    if not request.session.session_key:
        request.session.create()
    copied_post_data['file_session_key'] = request.session.session_key
    copied_post_data['chara_count'] = len(copied_post_data.get('source_text'))
    #get ipaddress
    copied_post_data['ip_address'] = lib.translator.get_ip_address(request)

    form = TextForm(copied_post_data, initial=default_form_value)

    jotai = bool(copied_post_data.get('jotai') == "true")

    if form.is_valid():
        form.save()
        transed_text = lib.translator.translate_text_by_google(copied_post_data.get('source_text'),
                                                               copied_post_data.get('source_lang'),
                                                               copied_post_data.get('target_lang'),
                                                               jotai,
                                                               pseudo=False)
        result = {"result": "success", "text": transed_text}
    else:
        message = ""
        for error in form.errors:
            message = message + form.errors[error]
        result = {"result": "error", "text": message}
    return JsonResponse(result)

def upload_glossary(request):
    """upload glossary"""

    #Set the session key to POST
    copied_post_data = request.POST.copy()
    copied_post_data['status'] = 300
    if request.FILES:
        form = GlossaryForm(copied_post_data, request.FILES)
        if form.is_valid():
            form.save()
            result = {"type": "success", "message": ["Uploaded"]}
        else:
            message = ""
            for error in form.errors:
                message = message + form.errors[error]
            result = {"type": "danger", "message": message}
        return JsonResponse(result)#この段階でmessageがstrからarrayになる　なぜ？
    else:
        return JsonResponse({"type": "danger", "message": ["File is not selected"]})

def upload_file(request):
    """upload file"""
    default_form_value = {'target_lang':'ja'}
    if request.FILES:
        #Set the session key to POST
        copied_post_data = request.POST.copy()
        if not request.session.session_key:
            request.session.create()
        copied_post_data['file_session_key'] = request.session.session_key

        #get ipaddress
        copied_post_data['ip_address'] = lib.translator.get_ip_address(request)

        jotai = bool(copied_post_data.get('jotai') == "true")
        copied_post_data['change_to_jotai'] = jotai
        form = DocumentForm(copied_post_data, request.FILES, initial=default_form_value)

        if form.is_valid():
            form.save()
            result = {"type": "success", "message": ["Uploaded"]}
        else:
            message = ""
            for error in form.errors:
                message = message + form.errors[error]
            result = {"type": "danger", "message": message}
        return JsonResponse(result)#この段階でmessageがstrからarrayになる　なぜ？
    else:
        return JsonResponse({"type": "danger", "message": ["File is not selected"]})

def file_tra(request, file_id):
    """translate file"""
    file = File.objects.get(pk=file_id)
    file.status = 1
    file.save()
    lib.translator.translate_file(file_id)
    return HttpResponse()

def glossary_del(request, glossary_id):
    """delete glossary"""
    result = lib.glossary.delete_glossary_fron_google(glossary_id)
    if result:
        blob_name = lib.glossary.delete_glossary_file(glossary_id)
        lib.glossary.delete_glossary_file_from_google(blob_name)
    else:
        lib.glossary.set_glossary_status(glossary_id, 305)

    return HttpResponse()

def file_del(request, file_id):
    """delete file"""
    lib.translator.set_delete_flag(file_id)
    return HttpResponse()


def get_file_list_data(request):
    """get file list"""
    tbody_html = lib.translator.create_file_list_tbody_html(request, STATUS)
    return JsonResponse(tbody_html)

def get_glossary_list_data(request):
    """get glossary list"""
    tbody_html = lib.glossary.create_glossary_list_tbody_html(request, STATUS)
    return JsonResponse(tbody_html)


def file_download(request, file_id):
    """file download"""
    file = File.objects.get(pk=file_id)

    root, ext = os.path.splitext(str(file.document))
    translated_file_path = root + ".out" + ext

    with open(os.path.join(settings.MEDIA_ROOT, translated_file_path), 'rb') as in_file:
        binary = io.BytesIO(in_file.read())

    mime = mimetypes.guess_type(translated_file_path)
    response = HttpResponse(binary, content_type=mime[0])
    response["Content-Disposition"] = 'filename=' + urllib.parse.quote(str(file))
    return response
