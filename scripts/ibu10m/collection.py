from __future__ import annotations

import os
from enum import Enum
from glob import glob

import pystac
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.link import Link

from .constants import (
    CLMS_LICENSE,
    COLLECTION_DESCRIPTION,
    COLLECTION_EXTENT,
    COLLECTION_ID,
    COLLECTION_KEYWORDS,
    COLLECTION_SUMMARIES,
    COLLECTION_TITLE,
    IBU10M_HOST_AND_LICENSOR,
    STAC_DIR,
    WORKING_DIR,
)


class IBUItemAssets(Enum):
    dataset = AssetDefinition({"title": "Map", "media_type": pystac.MediaType.GEOTIFF, "roles": ["data"]})
    database = AssetDefinition({"title": "Map Database", "media_type": "application/dbf", "roles": ["metadata"]})
    worldfile = AssetDefinition({"title": "Map World File", "media_type": pystac.MediaType.TEXT, "roles": ["metadata"]})


def create_core_collection() -> pystac.Collection:
    return pystac.Collection(
        id=COLLECTION_ID,
        description=COLLECTION_DESCRIPTION,
        extent=COLLECTION_EXTENT,
        title=COLLECTION_TITLE,
        keywords=COLLECTION_KEYWORDS,
        providers=[IBU10M_HOST_AND_LICENSOR],
        summaries=COLLECTION_SUMMARIES,
    )


def add_item_assets_to_collection(collection: pystac.Collection, item_asset_class: Enum) -> None:
    item_assets = ItemAssetsExtension.ext(collection, add_if_missing=True)
    item_assets.item_assets = {asset.name: asset.value for asset in item_asset_class}


def add_links_to_collection(collection: pystac.Collection, link_list: list[Link]) -> None:
    for link in link_list:
        collection.links.append(link)


def add_items_to_collection(collection: pystac.Collection, item_list: list[str]) -> None:
    for item in item_list:
        stac_object = pystac.read_file(item)
        collection.add_item(stac_object, title=stac_object.id)


def create_collection(item_list: list[str]) -> pystac.Collection:
    collection = create_core_collection()

    # extensions
    add_item_assets_to_collection(collection, IBUItemAssets)

    # links
    link_list = [CLMS_LICENSE]
    add_links_to_collection(link_list)

    # add items
    items = glob(item_list)
    add_items_to_collection(collection, items)

    collection_dir = os.path.join(WORKING_DIR, f"{STAC_DIR}/{COLLECTION_ID}")
    collection_path = os.path.join(collection_dir, f"{collection.id}.json")
    collection.set_self_href(collection_path)
    collection.save_object()
