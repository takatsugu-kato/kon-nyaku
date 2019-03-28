import json
import pytz
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from background_task import background
from django.core import serializers
from django.utils import dateformat

from translate.models import File
from translate.forms import DocumentForm
from lib.okapi import Okapi
from lib.xlf import Xlf

from .consts import STATUS

# Create your views here.
def file_list(request):
    """ファイルの一覧"""
    default_form_value = {'target_lang':'ja'}
    if request.FILES:
        form = DocumentForm(request.POST, request.FILES, initial=default_form_value)
        if form.is_valid():
            form.save()
    else:
        form = DocumentForm(initial=default_form_value)

    return render(request,
                  'translate/file_list.html',     # 使用するテンプレート
                  {'file_list_data': create_file_list_tbody_html(),
                   'form': form,
                   'STATUS': STATUS},
                 )


def file_tra(request, file_id):
    """ファイルの翻訳"""
    translate_xlf(file_id)
    return HttpResponse('ファイルの翻訳' + str(file_id))


def file_del(request, file_id):
    """ファイルの削除"""
    file = get_object_or_404(File, pk=file_id)
    file.delete()
    return HttpResponseRedirect('/translate/file')

@background(queue='translate_queue', schedule=5)
def translate_xlf(file_id):
    """
    Translate xlf file
    """
    file = File.objects.get(pk=file_id)
    to_trans_file = str(file.document)

    print("Translating {0}".format(to_trans_file))

    source_lang = file.source_lang
    target_lang = file.target_lang
    translation_model = "nmt"
    # to_trans_file = "./sample_file/test.docx"

    okapi_obj = Okapi(source_lang, target_lang)
    okapi_obj.create_xlf(to_trans_file)


    xlf_obj = Xlf(to_trans_file + ".xlf")
    xlf_obj.translate(translation_model, delete_format_tag=False, pseudo=True, django_file_obj=file)
    xlf_obj.back_to_xlf()

    okapi_obj.create_transled_file(to_trans_file + ".xlf")

def get_file_list_data(request):
    return JsonResponse(create_file_list_tbody_html())

def create_file_list_tbody_html():

    jst = pytz.timezone('Asia/Tokyo')

    files = File.objects.all().order_by('id')
    html = ""
    done_flag = 1
    for file in files:
        created_date = file.created_date.astimezone(jst)
        created_date_str = created_date.strftime('%Y-%m-%d %H:%M')
        modified_date = file.modified_date.astimezone(jst)
        modified_date_str = modified_date.strftime('%Y-%m-%d %H:%M')
        if file.status == 1:
            done_flag = 0
        html = html + '        <tr>\n'\
            '          <th scope="row">' + str(file.id) + '</th>\n'\
            '          <td>' + file.name + '</td>\n'\
            '          <td>' + file.source_lang + '</td>\n'\
            '          <td>' + file.target_lang + '</td>\n'\
            '          <td>' + STATUS[file.status] + '</td>\n'\
            '          <td>' + str(file.progress) + '</td>\n'\
            '          <td>' + created_date_str + '</td>\n'\
            '          <td>' + modified_date_str + '</td>\n'\
            '          <td>\n'\
            '            <a href="tra/' + str(file.id) + '" class="btn btn-outline-primary btn-sm">翻訳</a>\n'\
            '            <a href="del/' + str(file.id) + '" class="btn btn-outline-danger btn-sm">削除</a>\n'\
            '          </td>\n'\
            '        </tr>\n'
    return_json = {"html": html, "done_flag": done_flag}
    return return_json