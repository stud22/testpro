import zipfile
import csv
import os
from io import TextIOWrapper

from django.shortcuts import render
from django.core.files import File
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.conf import settings
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.list import ListView

from .models import Teacher, Subject
from .teachers_form import UploadFile, TeachersForm


class TeacherListView(ListView):
    model = Teacher
    template_name = 'accountInfo/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_name_chars = []
        subject_chars = []
        for row in Teacher.objects.values_list('last_name', flat=True).filter(
                last_name__isnull=False).exclude(last_name='').order_by('last_name').distinct():
            first_char = row.strip().upper()[0]
            if first_char not in last_name_chars:
                last_name_chars.append(first_char)
        for row in Subject.objects.values_list('name', flat=True).filter(
                name__isnull=False).exclude(name='').order_by('name').distinct():
            first_char = row.strip().upper()[0]
            if first_char not in subject_chars:
                subject_chars.append(first_char)
        context['last_name_chars'] = last_name_chars
        context['subject_chars'] = subject_chars
        return context

    def get_queryset(self):
        queryset = self.model.objects.all()
        if self.request.GET.get('val'):
            val = self.request.GET.get('val')
            if self.request.GET.get('type') and self.request.GET.get('type') == 'name':
                queryset = queryset.filter(last_name__istartswith=val)
            if self.request.GET.get('type') and self.request.GET.get('type') == 'subject':
                queryset = queryset.filter(subjects__name__istartswith=val)
        return queryset


class TeacherDetailView(DetailView):
    model = Teacher


class BulkImportView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = 'accountInfo/import.html'

    def get(self, request, *args, **kwargs):
        form = UploadFile()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        zippath = settings.MEDIA_ROOT.joinpath('tmp').joinpath('teachers.zip')
        form = UploadFile(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES['images']
            with open(zippath, 'wb+') as destination:
                for chunk in images.chunks():
                    destination.write(chunk)

            names = request.FILES['names']
            archive = zipfile.ZipFile(zippath, 'r')
            data_bytes = TextIOWrapper(request.FILES['names'].file,
                                       encoding='utf-8')
            data_reader = csv.DictReader(data_bytes)
        try:
            for row in data_reader:

                if row['First Name'].strip() == '' or row['Email Address'].strip() == '':
                    raise Exception('First Name / Email cant be blank')
                teacher = Teacher()
                teacher.first_name = row['First Name'].strip()
                teacher.last_name = row['Last Name'].strip()
                teacher.email = row['Email Address'].strip()
                teacher.phone = row['Phone Number'].strip()
                teacher.room_no = row['Room Number'].strip()
                teacher.save()
                subjects = row['Subjects taught'].split(',')
                if row['Profile picture'] in archive.namelist():
                    image = archive.open(row['Profile picture'], 'r')
                    df = File(image)
                    teacher.profile_picture.save(row['Profile picture'], df, save=True)
                for subj in subjects:
                    if subj != '':
                        subject, _ = Subject.objects.get_or_create(name=subj.strip().upper())
                        if teacher.subjects.count() < 5:
                            teacher.subjects.add(subject)
            messages.success(request, 'Data saved successfully')
        except Exception as e:
            messages.info(request, e)
        finally:
            # 634657778
            os.remove(zippath)
        return render(request, self.template_name, {'form': form})
