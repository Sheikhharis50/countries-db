"""Services used to fullfill address related needs"""

import json
import os
from abc import ABC, abstractmethod
from collections import OrderedDict
from importlib import import_module
from typing import Any

from countryinfo import CountryInfo
from i18naddress import load_validation_data
from slugify import slugify


async def services_similar(src: "AddressService", dest: "AddressService"):
    """Check wether source service countries are in destination service."""

    src_countries = await src.get_countries()
    dest_countries = await dest.get_countries()
    src_codes, dest_codes = src_countries.keys(), dest_countries.keys()

    for code in src_codes:
        if code in dest_codes:
            continue

        return False
    return True


class AddressService(ABC):
    """Abstract class to fetch countries and states."""

    @abstractmethod
    async def get_countries(self) -> dict[str, Any]:
        """Method to get all countries."""

    @abstractmethod
    async def get_states(self, country_code: str) -> dict[str, Any]:
        """Method to get all states against each country_code."""

    async def get_countries_with_states(self):
        """Get countries dictionary with it's states."""

        countries = await self.get_countries()

        # Appending states under each country.
        for country_code, country_name in countries.items():
            countries[country_code] = {
                "country_code": country_code,
                "country_name": country_name,
                "states": await self.get_states(country_code),
            }
        return countries

    async def export(self, path: str, countries: dict[str, Any]):
        """Export countries with it's states to given path."""

        with open(path, mode="w", encoding="utf8") as file:
            json_obj = json.dumps(countries, indent=4)
            file.write(json_obj)


class I18nAddressService(AddressService):
    """
    Service class which returns i18nAddress standard addresses using following python library
    https://pypi.org/project/google-i18n-address/1.0.4/
    """

    DISCARDED_COUNTRIES = (
        "all",
        "zz",
    )

    def __init__(self) -> None:
        self._db: dict[str, Any] = load_validation_data()

    async def _country_names(self):
        module = import_module("i18naddress")
        names = list(
            set(
                [
                    os.path.splitext(file_name)[0].upper()
                    for file_name in os.listdir(f"{module.__path__[0]}/data")
                    if file_name.endswith(".json")
                    and os.path.splitext(file_name)[0] not in self.DISCARDED_COUNTRIES
                ]
            )
        )
        names.sort()
        return names

    async def get_countries(self):
        return {code: self._db[code]["name"] for code in await self._country_names()}

    async def get_states(self, country_code: str):
        country_data: dict[str, Any] = self._db[country_code.upper()]
        keys = filter(None, country_data.get("sub_keys", "").split("~"))
        names = filter(None, country_data.get("sub_names", "").split("~"))
        return {key: name for key, name in zip(keys, names)}


class CountryInfoService(AddressService):
    """
    Service class which returns addresses using CountryInfo python library
    https://pypi.org/project/countryinfo/
    """

    async def get_countries(self) -> dict[str, Any]:
        instance = CountryInfo()
        countries = OrderedDict(sorted(instance.all().items()))

        return {
            country["ISO"]["alpha2"]: country["name"] for country in countries.values()
        }

    async def get_states(self, country_code: str) -> dict[str, Any]:
        def get_key(state: str):
            words = slugify(state).split("-")
            if len(words) > 1:
                return (words[0][0] + words[1][0]).upper()
            return words[0][:2].upper()

        try:
            country = CountryInfo(country_code.upper()).info() or {}
            return {get_key(state): state for state in country["provinces"]}
        except KeyError:
            return {}
