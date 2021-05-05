import re

from django.shortcuts import render, redirect
from invoker.models import SearchedPhoneNumberModel, NumberDetailModel, CnicNumbersModel, NetworkInformationModel
from khoojee.celery import find_number_details
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape


def get_database_content(phone_number):
    details = {}
    try:
        ref_phone_no = SearchedPhoneNumberModel.objects.get(phone_number=phone_number)

        phone_details = NumberDetailModel.objects.get(phone_number=ref_phone_no)
        try:
            cnic = phone_details.cnic.cnic_number
        except:
            cnic = None

        sim_details = {
            "phone_number": ref_phone_no.phone_number,
            "cnic": cnic,
            "date": phone_details.date,
            "name": phone_details.name,
            "first_name": phone_details.first_name,
            "last_name": phone_details.last_name,
            "address": phone_details.address,
            "address1": phone_details.address1,
            "address2": phone_details.address2,
            "city": phone_details.city,
            "other_phone": phone_details.other_phone,
        }
        network_details = {}
        try:
            ref_network = NetworkInformationModel.objects.get(phone_number=ref_phone_no)
            network_details["city"] = ref_network.city
            network_details["network"] = ref_network.network
            network_details["status"] = ref_network.status
        except:
            pass
        details = {
            "sim_details": sim_details,
            "network_details": network_details,
        }
    except SearchedPhoneNumberModel.DoesNotExist:
        pass
    return details


def home(request):
    if request.method == 'POST':
        content = {
            "has_error": True,
            "error_title": "",
            "error_message": "",
        }
        if 'phone_number' not in request.POST:
            content["error_title"] = "Phone number not found!"
            content["error_message"] = "Please enter phone number for search."
            return render(request, "pages/phone/main.html", content)

        if not request.POST["phone_number"]:
            content["error_title"] = "Phone number not found!"
            content["error_message"] = "Please enter phone number for search."
            return render(request, "pages/phone/main.html", content)

        phone_number = request.POST.get('phone_number', '')
        mobile_number_reg = '^((\+92)|(0092))-{0,1}\d{3}-{0,1}\d{7}$|^\d{11}$|^\d{10}$|^\d{4}-\d{7}$'
        phone_match = re.match(mobile_number_reg, phone_number)

        if not phone_match:
            content["error_title"] = "Invalid phone number provided!"
            content["error_message"] = 'Please provide correct phone number. Supported format [00923131234567, ' \
                                       '+923131234567, 03131234567, 3131234567]'
            return render(request, "pages/phone/main.html", content)

        allow_public = True
        if 'is_allowed' not in request.POST:
            allow_public = False
        try:
            records = SearchedPhoneNumberModel.objects.filter(
                phone_number=phone_number
            )
            if not records:
                find_number_details.delay(phone_number, allow_public)

        except SearchedPhoneNumberModel.DoesNotExist:
            find_number_details.delay(phone_number, allow_public)
        return redirect('sim_details/?phone_number=' + phone_number)

        # @TODO: Check results here if we already have mobile record in our database.
        # @TODO: Return user result from database

    return render(request, "pages/phone/main.html")


def sim_details_page_view(request):
    # @TODO: Three type of results
    # 1. Result found 2. In progress 3. Please search again
    mobile_number = None
    if "phone_number" in request.GET:
        mobile_number = request.GET["phone_number"]

        try:
            searched_term = SearchedPhoneNumberModel.objects.get(
                phone_number=mobile_number
            )

            if searched_term.is_search_completed:
                print("completed")
                if searched_term.details_found:
                    details = get_database_content(mobile_number)
                    content = {
                        "profile": True,
                        "mobile_number": mobile_number,
                        "details": details,
                    }
                    return render(request, "pages/phone/results.html", content)
                else:
                    content = {
                        "profile": False,
                        "mobile_number": mobile_number
                    }
                    return render(request, "pages/phone/results.html", content)
            else:
                content = {
                    "searching": True,
                    "mobile_number": mobile_number
                }
                return render(request, "pages/phone/results.html", content)
        except SearchedPhoneNumberModel.DoesNotExist:
            content = {
                "searching": True,
                "mobile_number": mobile_number
            }
            return render(request, "pages/phone/results.html", content)

    else:
        content = {
            "has_error": True,
            "error_message": 'Please provide phone number, no number found in request. Supported format '
                             '[00923131234567, +923131234567, 03131234567, 3131234567]'}
        return render(request, "pages/phone/main.html", content)
