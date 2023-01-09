"""Script which uses scrap app to fetch and export countries with states"""

import argparse
import asyncio
import os

from app.config import settings
from app.services import CountryInfoService, I18nAddressService


async def main(args):
    """Main execution of the program"""

    match args.service_name:
        case "countryinfo":
            service = CountryInfoService()
        case _:
            service = I18nAddressService()

    path = os.path.join(settings.DATA_DIR, f"output.{args.service_name}.json")
    await service.export(path=path, countries=await service.get_countries_with_states())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "service_name",
        help="Service name which is used to output countries data.",
        choices=["countryinfo", "i18n"],
    )
    asyncio.run(main(parser.parse_args()))
