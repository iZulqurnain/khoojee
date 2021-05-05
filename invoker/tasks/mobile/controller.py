from django.db import IntegrityError

from invoker.core.phone.search import Search


class Controller:
    __MOBILE_NUMBER__ = None
    __ALLOW_PUBLIC__ = None

    def __init__(self, mobile_number, allow_public):
        self.__MOBILE_NUMBER__ = mobile_number
        self.__ALLOW_PUBLIC__ = allow_public

    def __check_record__(self):
        from invoker.models import SearchedPhoneNumberModel
        try:
            record = SearchedPhoneNumberModel.objects.filter(
                phone_number=self.__MOBILE_NUMBER__
            )
            if record:
                return True
            else:
                return False
        except SearchedPhoneNumberModel.DoesNotExist:
            return False

    def __add_phone_number__(self):
        from invoker.models import SearchedPhoneNumberModel

        try:
            SearchedPhoneNumberModel.objects.create(
                phone_number=self.__MOBILE_NUMBER__,
                is_public_allowed=self.__ALLOW_PUBLIC__,
            )
        except:
            print("Failed to add phone number in database.")

    def __start_search__(self):
        from invoker.models import SearchedPhoneNumberModel, NumberDetailModel, CnicNumbersModel, \
            NetworkInformationModel, \
            LocationGenderModel

        if self.__check_record__():
            print("Record already exists into database")
            return
        # Phone number added into database
        self.__add_phone_number__()

        search_object = Search(self.__MOBILE_NUMBER__)
        status_code, content = search_object.get_report()
        if not status_code:
            SearchedPhoneNumberModel.objects.filter(
                phone_number=self.__MOBILE_NUMBER__
            ).update(
                is_search_completed=True
            )
            print("Failed to scrap results from web")
            return
        try:
            ref_phone_record = SearchedPhoneNumberModel.objects.get(
                phone_number=self.__MOBILE_NUMBER__
            )
            pak_data = content["pak_data"]
            sim_info = content["sim_info"]
            cnic_info = content["cnic_info"]
            if "cnic" in pak_data:
                try:
                    ref_cnic_record = CnicNumbersModel.objects.create(
                        cnic_number=pak_data["cnic"]
                    )
                except IntegrityError:
                    ref_cnic_record = CnicNumbersModel.objects.get(
                        cnic_number=pak_data["cnic"]
                    )
                NumberDetailModel.objects.create(
                    phone_number=ref_phone_record,
                    cnic=ref_cnic_record,
                    date=pak_data["date"],
                    name=pak_data["name"],
                    address=pak_data["address"],
                    address1=pak_data["address1"],
                    address2=pak_data["address2"],
                    city=pak_data["city"],
                    other_phone=pak_data["other_phone"],
                    first_name=pak_data["first_name"],
                    last_name=pak_data["last_name"],

                )
                SearchedPhoneNumberModel.objects.filter(
                    phone_number=self.__MOBILE_NUMBER__
                ).update(
                    details_found=True
                )
                if cnic_info:
                    LocationGenderModel.objects.create(
                        cnic=ref_cnic_record,
                        tehsil=cnic_info["tehsil"],
                        division=cnic_info["division"],
                        province=cnic_info["province"],
                        gander=cnic_info["gander"],
                    )

            if sim_info:
                NetworkInformationModel.objects.create(
                    phone_number=ref_phone_record,
                    network=sim_info["network"],
                    city=sim_info["city"],
                    status=sim_info["status"],
                )
            SearchedPhoneNumberModel.objects.filter(
                phone_number=self.__MOBILE_NUMBER__
            ).update(
                is_search_completed=True,
            )

        except SearchedPhoneNumberModel.DoesNotExist:
            pass
        print("ALL GOOD!")

    def start(self):
        self.__start_search__()


def controller(mobile_number, allow_public):
    controller_object = Controller(mobile_number, allow_public)
    controller_object.start()
