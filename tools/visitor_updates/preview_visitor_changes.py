#!/usr/bin/env python3
"""Read-only preview of researched visitor fields against the laptop database.

No database, media or project file changes. Proposals are not verified facts;
review source notes and approve exact fields separately before any update.
"""
import csv
from collections import Counter
from datetime import datetime
import os
from pathlib import Path
import sys

# Compiled from the five source-linked research documents on 2026-11-06.
PROPOSALS = [
  {
    "id": 7622,
    "title": "Calle Ramos",
    "slug": "osm-node-12192549354",
    "field": "address",
    "proposed": "15 Ramos Subdivision, Kabankalan City",
    "notes": "Medium: the [business page](https://www.facebook.com/p/Calle-Ramos-61556818838081/) gives this address; the record's broad name/location is consistent but the exact pin was not independently verified.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7622,
    "title": "Calle Ramos",
    "slug": "osm-node-12192549354",
    "field": "barangay",
    "proposed": "Barangay 4",
    "notes": "Medium: [business page](https://www.facebook.com/p/Calle-Ramos-61556818838081/); same identity qualification.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7622,
    "title": "Calle Ramos",
    "slug": "osm-node-12192549354",
    "field": "phone",
    "proposed": "+63 917 772 3207",
    "notes": "Medium: [business page](https://www.facebook.com/p/Calle-Ramos-61556818838081/); confirm still current.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7631,
    "title": "Sol's Garden Caf\u00e9",
    "slug": "osm-node-12137330729",
    "field": "address",
    "proposed": "Don Emilio Village Phase 1, Kabankalan City",
    "notes": "High for broad location: [business page](https://www.facebook.com/p/Sols-Garden-Caf%C3%A9-100087570230355/) and [listing with nearby coordinates](https://restaurantguru.com/Sols-Garden-Cafe-Kabankalan); record's existing phone matches. Do not append an unverified street.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7631,
    "title": "Sol's Garden Caf\u00e9",
    "slug": "osm-node-12137330729",
    "field": "barangay",
    "proposed": "Barangay 9",
    "notes": "Medium: [listing](https://wanderboat.ai/restaurants/philippines/kabankalan/sol's-garden-cafe/4bGbcDfpQv-H8B7CDAQzjw) plus phone and nearby location match; not independently field-checked.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7771,
    "title": "Ample Corner",
    "slug": "osm-node-4567883293",
    "field": "address",
    "proposed": "Cordova Street, Kabankalan City",
    "notes": "High for broad location: [business page](https://www.facebook.com/AmpleCorner/) and [Foodpanda](https://www.foodpanda.ph/restaurant/k7ls/ample-corner-restaurant-cordova), whose listed coordinates are close to the record pin.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7771,
    "title": "Ample Corner",
    "slug": "osm-node-4567883293",
    "field": "barangay",
    "proposed": "Barangay 5",
    "notes": "Medium: [Foodpanda](https://www.foodpanda.ph/restaurant/k7ls/ample-corner-restaurant-cordova) explicitly lists Barangay 5 and nearby coordinates.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7771,
    "title": "Ample Corner",
    "slug": "osm-node-4567883293",
    "field": "phone",
    "proposed": "+63 961 952 0328",
    "notes": "Medium: [business page](https://www.facebook.com/AmpleCorner/); confirm still current.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7635,
    "title": "CityMall Kabankalan",
    "slug": "osm-way-519017326",
    "field": "barangay",
    "proposed": "Talubangi",
    "notes": "Medium: [tenant's official branch locator](https://branches.executiveoptical.com/) lists City Mall on Justice Perez Highway, Talubangi. Check against the existing mall pin.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7635,
    "title": "CityMall Kabankalan",
    "slug": "osm-way-519017326",
    "field": "phone",
    "proposed": "(034) 746-7967",
    "notes": "Medium: [city tourism directory](https://kabankalancity.gov.ph/tourism/resort-and-restaurants/) lists City Mall; directory date/current status unknown, confirm. Do not use a tenant's phone.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7636,
    "title": "Gaisano Grand Mall Kabankalan",
    "slug": "osm-way-247293840",
    "field": "barangay",
    "proposed": "Barangay 1",
    "notes": "Medium: [mall page](https://www.facebook.com/grand.kabankalan/) and [city directory](https://kabankalancity.gov.ph/tourism/resort-and-restaurants/); mapped mall pin is consistent.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7636,
    "title": "Gaisano Grand Mall Kabankalan",
    "slug": "osm-way-247293840",
    "field": "phone",
    "proposed": "(034) 471-3588",
    "notes": "Medium: [mall page](https://www.facebook.com/grand.kabankalan/); [city directory](https://kabankalancity.gov.ph/tourism/resort-and-restaurants/) instead lists 471-3580, so confirm before entry.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7633,
    "title": "Best Department Store",
    "slug": "osm-node-4567944690",
    "field": "address",
    "proposed": "Bonifacio Street, Kabankalan City",
    "notes": "Medium: [city directory](https://kabankalancity.gov.ph/tourism/resort-and-restaurants/) and [street directory](https://philippines-streets.openalfa.com/kabankalan-city/shopping); exact branch not independently field-checked.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7633,
    "title": "Best Department Store",
    "slug": "osm-node-4567944690",
    "field": "phone",
    "proposed": "(034) 471-2186",
    "notes": "Medium: [city directory](https://kabankalancity.gov.ph/tourism/resort-and-restaurants/); directory date unknown, confirm.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7654,
    "title": "BPI",
    "slug": "osm-way-1374319930",
    "field": "phone",
    "proposed": "(034) 441-3418",
    "notes": "Medium: [BPI's branch contact list](https://www2.bpi.com.ph/contactus/branches) lists Negros-Kabankalan on Guanzon Street; [location listing](https://www.helpmecovid.com/ph/168463_bpi-negros-kabankalan-branch-atm) is near the record's pin. BPI formats the number +633 444-13418; a [separate listing](https://zaubee.com/biz/bpi-negros-kabankalan-branch-jhbnl97v) gives the local formatting above. Confirm before calling.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7654,
    "title": "BPI",
    "slug": "osm-way-1374319930",
    "field": "website",
    "proposed": "https://www.bpi.com.ph/",
    "notes": "High for the bank's official site: [BPI](https://www2.bpi.com.ph/contactus/branches); branch match as above.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7687,
    "title": "Holy Mother of Mercy Hospital",
    "slug": "osm-node-12136667737",
    "field": "address",
    "proposed": "Highway Mabinay, Don Emilio Village, Kabankalan City",
    "notes": "High for location: [hospital group's 2026 posts](https://www.findhealthclinics.com/PH/Kabankalan/549587705424400/Holy-Mother-of-Mercy-Group-of-Hospitals), with [nearby mapped coordinates](https://maps.me/catalog/health/amenity-hospital/philippines/kabankalan-198506059/). Existing address is just `9`; replacement requires review.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7687,
    "title": "Holy Mother of Mercy Hospital",
    "slug": "osm-node-12136667737",
    "field": "barangay",
    "proposed": "Barangay 9",
    "notes": "High for location: [hospital group](https://www.findhealthclinics.com/PH/Kabankalan/549587705424400/Holy-Mother-of-Mercy-Group-of-Hospitals).",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7687,
    "title": "Holy Mother of Mercy Hospital",
    "slug": "osm-node-12136667737",
    "field": "phone",
    "proposed": "(034) 471-8881",
    "notes": "Medium: [hospital group](https://www.findhealthclinics.com/PH/Kabankalan/549587705424400/Holy-Mother-of-Mercy-Group-of-Hospitals) lists a range 8881\u20138885; confirm current before publishing, especially for emergency use.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7687,
    "title": "Holy Mother of Mercy Hospital",
    "slug": "osm-node-12136667737",
    "field": "website",
    "proposed": "https://holymotherofmercyhospital.com/",
    "notes": "Medium: [hospital group](https://www.findhealthclinics.com/PH/Kabankalan/549587705424400/Holy-Mother-of-Mercy-Group-of-Hospitals) lists it; check site remains active.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7704,
    "title": "Lea Jane Beauty Salon and Barber Shop",
    "slug": "osm-node-4567944590",
    "field": "category",
    "proposed": "Barber / Hair Salon",
    "notes": "Medium: the name and [business listing](https://xn--zlat-strnky-r7a3h.cybo.com/PH/kabankalan/kr%C3%A1sa-&-l%C3%A1zn%C4%9B) describe the service. Confirm this exact category exists in the live database. Do not infer a street: sources disagree.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7787,
    "title": "Melting Pot",
    "slug": "osm-node-5487360540",
    "field": "barangay",
    "proposed": "Barangay 7",
    "notes": "Medium: [city directory](https://kabankalancity.gov.ph/tourism/resort-and-restaurants/) lists Melting Pot on Rizal Street with the same phone already in the report.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7790,
    "title": "Perico",
    "slug": "osm-node-4567933293",
    "field": "address",
    "proposed": "Justice J.Y. Perez Highway, Kabankalan City",
    "notes": "High for broad street: [business page](https://www.facebook.com/PericoRestaurant/about/) and [separate listing with nearby pin](https://philippines.worldplaces.me/hotels-in-kabankalan/41598788-perico-restaurant.html).",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7790,
    "title": "Perico",
    "slug": "osm-node-4567933293",
    "field": "phone",
    "proposed": "+63 970 234 4562",
    "notes": "Medium: [business page](https://www.facebook.com/PericoRestaurant/about/); a [separate listing](https://philippines.worldplaces.me/hotels-in-kabankalan/41598788-perico-restaurant.html) gives a different landline, so confirm current contact.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 1,
    "title": "Kabankalan Plaza",
    "slug": "osm-way-247293144",
    "field": "category",
    "proposed": "Park",
    "notes": "Medium: [Mapcarta](https://mapcarta.com/W247032203) describes Kabankalan Plaza as a park. Confirm this category exists and is the appropriate live category; do not create it automatically.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 1703,
    "title": "Mag Aso Falls",
    "slug": "osm-node-3369728379",
    "field": "address",
    "proposed": "Sitio Dug-anon, Barangay Oringao, Kabankalan City",
    "notes": "Medium: [2025 travel article](https://vismin.ph/2025/must-visit-waterfalls-in-negros-occidental/) identifies the site; existing general address is not empty and must be reviewed before replacement.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 1703,
    "title": "Mag Aso Falls",
    "slug": "osm-node-3369728379",
    "field": "barangay",
    "proposed": "Oringao",
    "notes": "High for broad location: [SunStar](https://www.sunstar.com.ph/bacolod/local-news/mag-aso-falls-at-barangay-oringao).",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 1704,
    "title": "CPSU Museum",
    "slug": "osm-node-11425438071",
    "field": "barangay",
    "proposed": "Camingawan",
    "notes": "Medium: [CPSU's official site](https://v1.cpsu.edu.ph/) lists its main campus in Camingawan; the museum's association with that campus and location should be confirmed before entry.",
    "document": "VISITOR_INFORMATION_RESEARCH.md"
  },
  {
    "id": 7627,
    "title": "La Familia",
    "slug": "osm-node-12233549233",
    "field": "phone",
    "proposed": "+63 956 326 3857",
    "notes": "Medium: [restaurant listing](https://restaurantguru.com/La-Familia-Cafe-Kabankalan) gives coordinates approximately 10 metres from the record pin; [Waze](https://www.waze.com/live-map/directions/ph/western-visayas/kabankalan-city/la-familia-cafe?to=place.ChIJ0drMcqYTrDMRosB-bHJiJ7o) lists the same location. Confirm the number is still active.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7644,
    "title": "Aquanikk Purified Water",
    "slug": "osm-node-4982134423",
    "field": "address",
    "proposed": "Rizal Street, Kabankalan City",
    "notes": "Medium: [business directory](https://www.puertoparrot.com/services/1039/20) names Aquanikk and Rizal Street; [mapped street listing](https://philippines-streets.openalfa.com/streets/bangga-erams-kabankalan-barangay-9-kabankalan-city) is consistent with the approximate pin. Verify current branch.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7644,
    "title": "Aquanikk Purified Water",
    "slug": "osm-node-4982134423",
    "field": "phone",
    "proposed": "(034) 213-4057",
    "notes": "Medium: [business directory](https://www.puertoparrot.com/services/1039/20), publication date unknown. Confirm active and exact branch.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7646,
    "title": "Ava Water Refilling Station",
    "slug": "osm-node-5719244321",
    "field": "address",
    "proposed": "3 Coloso Street, Kabankalan City",
    "notes": "Medium: [business page](https://www.facebook.com/avawaterrefillingstation/) states this. Pin is near the street but exact site is not independently verified.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7646,
    "title": "Ava Water Refilling Station",
    "slug": "osm-node-5719244321",
    "field": "phone",
    "proposed": "+63 917 790 0383",
    "notes": "Medium: [business page](https://www.facebook.com/avawaterrefillingstation/), confirm number and branch.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7649,
    "title": "Bantayan Public Market",
    "slug": "osm-way-283651062",
    "field": "barangay",
    "proposed": "Bantayan",
    "notes": "Medium: [city's Barangay Bantayan profile](https://kabankalancity.gov.ph/barangay/barangay-bantayan/) mentions its market; [map listing](https://philippines-streets.openalfa.com/kabankalan-city/other) lists the Kabankalan market by that name. Exact pin should be checked. **Not the Bantayan market in Cebu.**",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7661,
    "title": "Camingawan Public Market",
    "slug": "osm-way-246338355",
    "field": "barangay",
    "proposed": "Camingawan",
    "notes": "Medium: [city barangay profile](https://kabankalancity.gov.ph/barangay/barangay-camingawan/) mentions its market; [Kabankalan map listing](https://philippines-streets.openalfa.com/kabankalan-city/other) names the market. Exact pin needs checking.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7696,
    "title": "Kabankalan City Hospital",
    "slug": "osm-way-838905925",
    "field": "barangay",
    "proposed": "Tabugon",
    "notes": "High: [hospital page](https://www.facebook.com/kchospital2000/) and [PhilHealth list](https://www.philhealth.gov.ph/partners/providers/facilities/accredited/DENTAL_093026.pdf) give Tabugon; [map](https://www.openstreetmap.org/way/838905925) matches the record's OSM identity.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7696,
    "title": "Kabankalan City Hospital",
    "slug": "osm-way-838905925",
    "field": "address",
    "proposed": "Purok Mangga, Barangay Tabugon, Kabankalan City",
    "notes": "High for broad address: [hospital page](https://www.facebook.com/kchospital2000/) and [PhilHealth](https://www.philhealth.gov.ph/partners/providers/facilities/accredited/DENTAL_093026.pdf). Existing `Tapi - Tabugon` is nonempty: review before replacing or combining.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7703,
    "title": "Landbank",
    "slug": "osm-node-4579207691",
    "field": "address",
    "proposed": "Jomabo Building, Tan Lorenzo corner Guanzon Streets, Kabankalan City",
    "notes": "Medium-high: [Landbank office list](https://www.landbank.com/images/inner_template/1711512118_09_List%20of%20Offices.pdf) and [nearby-coordinate listing](https://landbank.banklocationmaps.com/en/branch/913701-lbp-branch-jomabo-building-tan-lorenzo-corner-guanzon-sts-kabankalan-city). Verify current office location.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7703,
    "title": "Landbank",
    "slug": "osm-node-4579207691",
    "field": "barangay",
    "proposed": "Barangay 3",
    "notes": "Medium: [Landbank office list](https://www.landbank.com/images/inner_template/1711512118_09_List%20of%20Offices.pdf); nearby ATM information in the map listing refers to Barangay 2 and is not evidence for the branch. Confirm.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7703,
    "title": "Landbank",
    "slug": "osm-node-4579207691",
    "field": "phone",
    "proposed": "(034) 471-2315",
    "notes": "Medium: [Landbank office list](https://www.landbank.com/images/inner_template/1711512118_09_List%20of%20Offices.pdf); publication date and current line need confirmation.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7734,
    "title": "Pico Ads",
    "slug": "osm-node-4567933297",
    "field": "address",
    "proposed": "Aquiles Zayco Avenue, Kabankalan City",
    "notes": "Medium: [business page](https://www.facebook.com/p/Pico-AdsGraphics-100057032127031/) and [Yellow Pages](https://www.yellow-pages.ph/business/pico-ads-graphics) list the same business name and road; exact pin needs confirmation.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7734,
    "title": "Pico Ads",
    "slug": "osm-node-4567933297",
    "field": "phone",
    "proposed": "+63 977 329 7200",
    "notes": "Medium: [business page](https://www.facebook.com/p/Pico-AdsGraphics-100057032127031/); [Yellow Pages](https://www.yellow-pages.ph/business/pico-ads-graphics) lists different numbers. Verify branch and current contact.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7738,
    "title": "Producers Bank",
    "slug": "osm-node-4867384421",
    "field": "address",
    "proposed": "Producers Bank Building, Aquiles Zayco Avenue, Kabankalan City",
    "notes": "Medium: [bank's 2026 directory](https://www.producersbank.com.ph/branch-directory/) and [local bank listing](https://www.cybo.com/PH/hinoba-an/banks/?p=4) name the Kabankalan branch; exact pin requires confirmation. [Western Union](https://location.westernunion.com/ph/central-visayas/mabinay?page=4&country=PH&q=Mabinay,+Negros+Oriental,+Philippines) lists a different building, possibly historical.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7738,
    "title": "Producers Bank",
    "slug": "osm-node-4867384421",
    "field": "barangay",
    "proposed": "Barangay 1",
    "notes": "Medium: [bank's 2026 directory](https://www.producersbank.com.ph/branch-directory/); branch match requires confirmation.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7738,
    "title": "Producers Bank",
    "slug": "osm-node-4867384421",
    "field": "phone",
    "proposed": "(034) 485-4632",
    "notes": "Medium: [bank's 2026 directory](https://www.producersbank.com.ph/branch-directory/); verify it applies to this pin and is current.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7764,
    "title": "Triumph Hardware",
    "slug": "osm-node-4867384424",
    "field": "address",
    "proposed": "Purok Buri, Hi-way Mabinay, Kabankalan City",
    "notes": "Medium-high: [business site](http://www.bacolodtriumph.com/) and [listing with nearby coordinates](https://soamaps.com/country/PH/170103/triumph-hardware-kabankalan) match the Kabankalan branch, not its separate Binicuil branch.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7764,
    "title": "Triumph Hardware",
    "slug": "osm-node-4867384424",
    "field": "barangay",
    "proposed": "Barangay 4",
    "notes": "Medium: [business site](http://www.bacolodtriumph.com/) lists the Kabankalan branch in Barangay 4; pin match as above.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7764,
    "title": "Triumph Hardware",
    "slug": "osm-node-4867384424",
    "field": "phone",
    "proposed": "(034) 471-0240",
    "notes": "Medium: [business site](http://www.bacolodtriumph.com/) and [nearby-coordinate listing](https://soamaps.com/country/PH/170103/triumph-hardware-kabankalan); confirm line is current.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md"
  },
  {
    "id": 7653,
    "title": "BDO - Guanzon Street",
    "slug": "osm-node-4567931191",
    "field": "phone",
    "proposed": "(034) 746-8529",
    "notes": "Medium: [listing with coordinates](https://philippines.worldplaces.me/review/85424230-bdo-unibank.html) matches the record pin closely; [BDO](https://www.bdo.com.ph/rrm00441) lists its Kabankalan location on Guanzon. Other sources give different numbers; confirm the line is current and for this branch. Do not apply to BDO 7652.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7663,
    "title": "Cebuana Lhullier",
    "slug": "osm-node-4567883295",
    "field": "address",
    "proposed": "Bonifacio corner Lirazan Streets, Kabankalan City",
    "notes": "Medium: [Yellow Pages](https://www.yellow-pages.ph/business/cebuana-lhuillier-1036/branches) and [nearby-location listing](https://nearbyph.com/personal-finance/pawn-shops/9.98702/122.81543/rizal-street-kabankalan-city-6111-philippines); verify exact site because there are several Cebuana branches.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7663,
    "title": "Cebuana Lhullier",
    "slug": "osm-node-4567883295",
    "field": "phone",
    "proposed": "(034) 746-8425",
    "notes": "Medium: [Yellow Pages](https://www.yellow-pages.ph/business/cebuana-lhuillier-1036/branches) associates it with the Bonifacio/Lirazan location; [2015 branch directory](https://www.listph.com/2015/09/list-of-cebuana-lhuillier-branches-negros-occidental.html) lists the same number for Kabankalan 1. Confirm current.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7671,
    "title": "DBP",
    "slug": "osm-node-4567933304",
    "field": "address",
    "proposed": "DBP Building, corner Lirazan and Bonifacio Streets, Kabankalan City",
    "notes": "Medium-high: [DBP's 2023 directory](https://www.dbp.ph/wp-content/uploads/2023/03/DBP-Citizens-Charter-List-of-Offices-2023.pdf) and [government procurement notice](https://notices.philgeps.gov.ph/GEPSNONPILOT/Tender/PrintableBidNoticeAbstractUI.aspx?refid=8733203); the map record is in the vicinity. Confirm the branch has not moved.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7671,
    "title": "DBP",
    "slug": "osm-node-4567933304",
    "field": "barangay",
    "proposed": "Barangay 4",
    "notes": "Medium: [DBP's 2023 directory](https://www.dbp.ph/wp-content/uploads/2023/03/DBP-Citizens-Charter-List-of-Offices-2023.pdf) identifies this barangay. A [secondary listing](https://dbp.banklocationmaps.com/en/branch/1003416-dbp-branch-cor-lirazan-bonifacio-sts) has a Barangay 9 breadcrumb; give preference to DBP but confirm.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7671,
    "title": "DBP",
    "slug": "osm-node-4567933304",
    "field": "phone",
    "proposed": "(034) 471-3170",
    "notes": "Medium: [DBP's 2023 directory](https://www.dbp.ph/wp-content/uploads/2023/03/DBP-Citizens-Charter-List-of-Offices-2023.pdf); verify current.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7686,
    "title": "HJ Hardware",
    "slug": "osm-node-4567948989",
    "field": "address",
    "proposed": "Lirazan Street, Kabankalan City",
    "notes": "Medium: [Yellow Pages](https://www.yellow-pages.ph/business/hj-hardware-lumber-gen-mdse) and [OSM-derived street listing](https://philippines-streets.openalfa.com/kabankalan-city/shopping). Verify exact shop before publishing.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7686,
    "title": "HJ Hardware",
    "slug": "osm-node-4567948989",
    "field": "phone",
    "proposed": "(034) 471-2592",
    "notes": "Medium: [Yellow Pages](https://www.yellow-pages.ph/business/hj-hardware-lumber-gen-mdse); confirm current.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7710,
    "title": "Lorenzo D. Zayco District Hospital",
    "slug": "osm-way-519187989",
    "field": "address",
    "proposed": "Sitio Mohon, Barangay Binicuil, Kabankalan City",
    "notes": "Medium: [PhilHealth 2026 facility list](https://www.philhealth.gov.ph/partners/providers/facilities/accredited/HOSP_053126.pdf) names the hospital and locality. Confirm exact current facility matches this pin: [another listing](https://philippines.worldplaces.me/places-in-kabankalan/44503118-lorenzo-d-zayco-district-hospital.html) places it elsewhere.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7710,
    "title": "Lorenzo D. Zayco District Hospital",
    "slug": "osm-way-519187989",
    "field": "barangay",
    "proposed": "Binicuil",
    "notes": "Medium: [PhilHealth 2026 facility list](https://www.philhealth.gov.ph/partners/providers/facilities/accredited/HOSP_053126.pdf); exact facility/pin needs confirmation.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7710,
    "title": "Lorenzo D. Zayco District Hospital",
    "slug": "osm-way-519187989",
    "field": "phone",
    "proposed": "(034) 471-2357",
    "notes": "Medium: [PhilHealth 2026 facility list](https://www.philhealth.gov.ph/partners/providers/facilities/accredited/HOSP_053126.pdf), but the [provincial 2020 directory](https://www.negros-occ.gov.ph/wp-content/uploads/2020/11/ARTA-PGNO-2020-final2-compressed_compressed_558-570.pdf) gives another number. Confirm the correct current number directly; do not label it as an emergency hotline.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7713,
    "title": "M. Lhuiller",
    "slug": "osm-node-4567933305",
    "field": "address",
    "proposed": "43 Bonifacio Street, Kabankalan City",
    "notes": "Medium: [Singtel's M. Lhuillier branch list](https://cdn1.singteldigital.com/content/dam/singtel/M_Lhuillier_branch_list.pdf) and [nearby-coordinate listing](https://nearbyph.com/personal-finance/pawn-shops/9.98702/122.81543/rizal-street-kabankalan-city-6111-philippines) identify Kabankalan 1 on Bonifacio. Confirm exact pin/current location.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7713,
    "title": "M. Lhuiller",
    "slug": "osm-node-4567933305",
    "field": "phone",
    "proposed": "(034) 471-2385",
    "notes": "Medium: [directory](https://www.puertoparrot.com/service/category/money-changer/kabankalan-city) lists the Kabankalan 1 remittance service; confirm the number directly and do not confuse with nearby Cebuana's.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7735,
    "title": "PNB",
    "slug": "osm-way-247033114",
    "field": "address",
    "proposed": "NOAC National Highway corner Guanzon Street, Kabankalan City",
    "notes": "Medium-high: [government-hosted PNB branch list](https://cms-cdn.e.gov.ph/Philhealth/pdf/aca_pnb.pdf) and [coordinate listing](https://pnb.banklocationmaps.com/en/branch/921432-pnb-branch-noac-national-highway-cor-guanzon-st-kabankalan-city) are consistent with the record's pin. The branch list is dated 2021; confirm it is still there.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7735,
    "title": "PNB",
    "slug": "osm-way-247033114",
    "field": "phone",
    "proposed": "(034) 471-2193",
    "notes": "Medium: [coordinate listing](https://pnb.banklocationmaps.com/en/branch/921432-pnb-branch-noac-national-highway-cor-guanzon-st-kabankalan-city); confirm current with PNB.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7768,
    "title": "Yamaha 3S Shop",
    "slug": "osm-node-4567933307",
    "field": "barangay",
    "proposed": "Barangay 3",
    "notes": "Medium-high: [Yamaha's dealer page](https://find-dealer.yamaha-motor.com.ph/yamaha-3s-shop-des-marketing-des-marketing-motorcycle-shop-brgy-3-kabankalan-city-299949/Home) identifies DES Marketing on Guanzon near Honda 3S, consistent with the pin. Existing address and phone remain untouched.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7779,
    "title": "De La Gente Pizza",
    "slug": "osm-node-12126355902",
    "field": "phone",
    "proposed": "+63 921 614 5688",
    "notes": "Medium: [Cybo](https://www.cybo.com/PH/kabankalan/food-delivery-services/) identifies a branch on Aquiles Street, consistent with the recorded avenue. Verify exact branch and current line before entry.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7795,
    "title": "Wow Restaurant",
    "slug": "osm-node-7830079848",
    "field": "address",
    "proposed": "Guanzon Street, Kabankalan City",
    "notes": "Medium: [restaurant listing](https://restaurantguru.com/WOW-Restaurant-and-Event-Center-Kabankalan) has coordinates close to the record pin, and [2018 directory](https://negrosfindr.com/listings/wow-restaurant-and-event-center-kabankalan-city/) lists this road. Confirm the venue is the same.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7795,
    "title": "Wow Restaurant",
    "slug": "osm-node-7830079848",
    "field": "barangay",
    "proposed": "Binicuil",
    "notes": "Medium: [restaurant listing](https://restaurantguru.com/WOW-Restaurant-and-Event-Center-Kabankalan) and [2018 directory](https://negrosfindr.com/listings/wow-restaurant-and-event-center-kabankalan-city/); exact pin/current site should still be confirmed.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7795,
    "title": "Wow Restaurant",
    "slug": "osm-node-7830079848",
    "field": "phone",
    "proposed": "+63 907 473 4586",
    "notes": "Medium: [restaurant listing](https://restaurantguru.com/WOW-Restaurant-and-Event-Center-Kabankalan). [2018 directory](https://negrosfindr.com/listings/wow-restaurant-and-event-center-kabankalan-city/) lists another number, so confirm before entry.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md"
  },
  {
    "id": 7625,
    "title": "daily brew",
    "slug": "osm-node-4567933294",
    "field": "address",
    "proposed": "Guanzon Street, Kabankalan City",
    "notes": "Medium: [business directory](https://www.findglocal.com/PH/Kabankalan/173103-7) names Daily Brew on Guanzon, consistent with the [OSM street listing](https://philippines-streets.openalfa.com/kabankalan-city/eating-drinking). Verify exact venue and current location.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7626,
    "title": "Kape Centrale",
    "slug": "osm-node-12159153690",
    "field": "address",
    "proposed": "Guanzon corner Rizal Street, Kabankalan Public Plaza, Kabankalan City",
    "notes": "Medium-high: [business page](https://www.facebook.com/KapeCentrale/) gives the address; [listing with coordinates](https://zaubee.com/biz/kape-centrale-kidjlcg7) is near this record. Keep **phone on hold**: the [2019 listing](https://negrosfindr.com/listings/kape-centrale-kabankalan/) and [restaurant directory](https://restaurantguru.com/Kape-Centrale-Kabankalan) differ.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7626,
    "title": "Kape Centrale",
    "slug": "osm-node-12159153690",
    "field": "email",
    "proposed": "kapecentrale@gmail.com",
    "notes": "Medium-high: [business page](https://www.facebook.com/KapeCentrale/) lists this email; confirm it is still monitored and belongs to this venue.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7629,
    "title": "Redbucks",
    "slug": "osm-node-4579164597",
    "field": "address",
    "proposed": "Crossing Coronacion, Guanzon Street, Kabankalan City",
    "notes": "Medium: [Yelp](https://www.yelp.com/biz/redbuck-s-cafe-kabankalan) and [location listing](https://menuweb.menu/list/88388736/restaurants-kabankalan) describe a caf\u00e9 near the record pin. Same business/branch needs confirmation. Keep **phone on hold**: they list different numbers.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7643,
    "title": "alton's bar",
    "slug": "osm-node-4196577091",
    "field": "barangay",
    "proposed": "Barangay 9",
    "notes": "Medium: [restaurant-management article](https://itsourcecode.com/free-projects/fyp/online-restaurant-management-system-documentation-chapter-1) locates Alton's near Zaycoland in Barangay 9; [map listing](https://hi.maps.me/maps/country-philippines/city-kabankalan-198506059/) places Alton's near this pin. Verify that this is the same venue and remains current.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7647,
    "title": "Avon",
    "slug": "osm-node-4579156697",
    "field": "address",
    "proposed": "Tan Lorenzo Street, Kabankalan City",
    "notes": "Medium: [Avon beauty-center directory](https://www-o.avon.ph/PRSuite/beautycenters.page) identifies the center behind Landbank (search-indexed entry; direct page returned HTTP 500 during review); [imported map listing](https://philippines-streets.openalfa.com/kabankalan-city/shopping) is consistent. Confirm exact branch, since an [older directory](https://www.businesslist.ph/location/kabankalan) gives another address.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7647,
    "title": "Avon",
    "slug": "osm-node-4579156697",
    "field": "barangay",
    "proposed": "Barangay 3",
    "notes": "Medium: [Avon beauty-center directory](https://www-o.avon.ph/PRSuite/beautycenters.page); verify it still corresponds to the record pin.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7647,
    "title": "Avon",
    "slug": "osm-node-4579156697",
    "field": "phone",
    "proposed": "(034) 746-7129",
    "notes": "Medium: [Avon beauty-center directory](https://www-o.avon.ph/PRSuite/beautycenters.page); an older directory lists another number. Confirm current line.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7648,
    "title": "Bank of Commerce",
    "slug": "osm-way-1374316232",
    "field": "barangay",
    "proposed": "Barangay 2",
    "notes": "Medium: [PhilHealth's 2024 branch list](https://www.philhealth.gov.ph/partners/collecting/aca_Bank-of-Commerce.pdf) lists the Kabankalan branch on Guanzon; [BIR's 2023 bank list](https://bir-cdn.bir.gov.ph/local/pdf/RDO%2078_2023.pdf) also lists the branch on Guanzon. Confirm that the mapped record is the branch, not the separately listed Kabilog ATM. Existing address is unchanged.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7657,
    "title": "Bubbles & Blossom",
    "slug": "osm-node-4579164595",
    "field": "address",
    "proposed": "Guanzon Street, Kabankalan City",
    "notes": "Medium: [listing near Shell](https://philippines.worldplaces.me/review/114286449-shell.html) is consistent with the [map record](https://philippines-streets.openalfa.com/kabankalan-city/shopping). Confirm business and pin; no phone proposed from the 2016 source.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7664,
    "title": "CHA-ROSE",
    "slug": "osm-node-4567883291",
    "field": "address",
    "proposed": "Near Kabankalan Public Market, Kabankalan City",
    "notes": "Medium: [China Bank's 2026 merchant directory](https://www.chinabank.ph/library/pos-cash-on-demand-as-of-april-2026) lists New Cha-Rose Store at New Public Market, and [map](https://mapcarta.com/W624985029) shows CHA-ROSE nearby. Exact branch match should be confirmed.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7664,
    "title": "CHA-ROSE",
    "slug": "osm-node-4567883291",
    "field": "barangay",
    "proposed": "Barangay 1",
    "notes": "Medium: [China Bank's 2026 directory](https://www.chinabank.ph/library/pos-cash-on-demand-as-of-april-2026) lists New Cha-Rose Store in Barangay 1. Confirm this is the record's store.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7697,
    "title": "Kabankalan Public Market",
    "slug": "osm-way-624985029",
    "field": "barangay",
    "proposed": "Barangay 1",
    "notes": "Medium-high: [SunStar](https://www.sunstar.com.ph/more-articles/-charges-mulled-vs-man-who-set-vendor-on-fire) reports the public market on Tan Lorenzo Street in Barangay 1, consistent with [this OSM market](https://mapcarta.com/W624985029). Existing street address stays as recorded.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7718,
    "title": "Motorstar - Guanzon Street",
    "slug": "osm-node-6440009203",
    "field": "barangay",
    "proposed": "Barangay 3",
    "notes": "Medium: [business page](https://www.facebook.com/motorstarkabankalan/posts) lists Motorstar on Guanzon in Barangay 3. Confirm exact site, because a second Motorstar record (7717) exists.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7718,
    "title": "Motorstar - Guanzon Street",
    "slug": "osm-node-6440009203",
    "field": "phone",
    "proposed": "+63 933 828 7298",
    "notes": "Medium: [business page](https://www.facebook.com/motorstarkabankalan/posts); confirm it is current and belongs to 7718, not automatically 7717.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7728,
    "title": "Petron - Rizal Street",
    "slug": "osm-way-1324320658",
    "field": "barangay",
    "proposed": "Barangay 7",
    "notes": "Medium: [Petron station list](https://www.petron.com/wp-content/uploads/2024/09/Partcipating-Station-and-Outlet-DTI.pdf) and [DOE 2023 list](https://prod-cms.doe.gov.ph/documents/d/oimb/2023-list_petron-corporation-11062023-pdf) list a Petron station on Rizal Street in Barangay 7. Verify this is the same station as the record.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7729,
    "title": "Petron - Justice Y. Perez Avenue",
    "slug": "osm-way-247032426",
    "field": "barangay",
    "proposed": "Barangay 2",
    "notes": "Medium: [Petron's 2026 list](https://www.petron.com/wp-content/uploads/2026/04/Visayas.pdf) lists CALM station at Jesus Perez corner Guanzon, Barangay 2. Confirm exact record pin before assigning.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7739,
    "title": "Puregold",
    "slug": "osm-way-839116971",
    "field": "phone",
    "proposed": "0909 451 0388",
    "notes": "Medium: [Cybo](https://www.cybo.com/PH-biz/puregold-kabankalan) lists a Guanzon store near the record pin and an additional landline. Verify the number is current and for the exact outlet.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7744,
    "title": "Rusco Motors",
    "slug": "osm-node-6440009199",
    "field": "phone",
    "proposed": "(034) 471-3445",
    "notes": "Medium: [Yellow Pages](https://www.yellow-pages.ph/business/rusco-motors-inc-kabankalan) names Rusco on Guanzon, matching the recorded road. Confirm exact outlet and current number; do not transfer it to Rusi (7745).",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7750,
    "title": "Shell",
    "slug": "osm-way-247030664",
    "field": "address",
    "proposed": "Guanzon corner Tan Lorenzo Streets, Kabankalan City",
    "notes": "High for road-level match: [Shell's station locator](https://find.shell.com/ph/fuel/10022022-sh-guanzon-tan-lorenzo/en_PH) gives coordinates close to the record pin. Existing Guanzon address is nonempty, so review before enriching it.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7750,
    "title": "Shell",
    "slug": "osm-way-247030664",
    "field": "phone",
    "proposed": "(034) 471-2510",
    "notes": "Medium-high: [Shell's station locator](https://find.shell.com/ph/fuel/10022022-sh-guanzon-tan-lorenzo/en_PH); confirm current. Do not use the different J.Y. Perez branch number.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7753,
    "title": "Super A's",
    "slug": "osm-node-4567883297",
    "field": "address",
    "proposed": "Lirazan Street, Kabankalan City",
    "notes": "Medium-high: [business site](https://www.superascommercial.com/) and [map listing](https://philippines-streets.openalfa.com/kabankalan-city/shopping) name Super A's on Lirazan. Confirm the exact pin.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7753,
    "title": "Super A's",
    "slug": "osm-node-4567883297",
    "field": "website",
    "proposed": "https://www.superascommercial.com/",
    "notes": "Medium: [business site](https://www.superascommercial.com/); confirm exact shop match and site is maintained.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7762,
    "title": "Total - Aquiles-Zayco Avenue",
    "slug": "osm-way-814071606",
    "field": "barangay",
    "proposed": "Barangay 4",
    "notes": "Medium: [directory](https://www.puertoparrot.com/service/category/gasoline-station/kabankalan-city) lists Total at Aquiles-Zayco corner Lirazan in Barangay 4; [separate listing](https://soamaps.com/country/PH/169437/sea-oil-gas-station) gives coordinates very close to this pin. Confirm current operator and branch.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7762,
    "title": "Total - Aquiles-Zayco Avenue",
    "slug": "osm-way-814071606",
    "field": "phone",
    "proposed": "0917 321 2160",
    "notes": "Medium: [directory](https://www.puertoparrot.com/service/category/gasoline-station/kabankalan-city); listing age unknown, verify it is active before entry.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7776,
    "title": "Chicken Ati-Atihan",
    "slug": "osm-node-4579156693",
    "field": "address",
    "proposed": "Guanzon Street, Kabankalan City",
    "notes": "Medium: [city directory](https://kabankalancity.gov.ph/tourism/resort-and-restaurants/) and [listing near record coordinates](https://wanderboat.ai/restaurants/philippines/kabankalan/chicken-ati-atihan-restaurant/D0JwiMuFQ3eBgL73D_S4Og). Confirm exact venue. Sources disagree on contact; do not add a phone without checking.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7776,
    "title": "Chicken Ati-Atihan",
    "slug": "osm-node-4579156693",
    "field": "barangay",
    "proposed": "Barangay 2",
    "notes": "Medium: [city directory](https://kabankalancity.gov.ph/tourism/resort-and-restaurants/) gives Barangay 2 for its Guanzon Chicken Ati-Atihan. Confirm exact venue.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7778,
    "title": "CPSU - Cafeteria",
    "slug": "osm-node-5328932823",
    "field": "barangay",
    "proposed": "Camingawan",
    "notes": "Medium: [CPSU describes its cafeteria](https://cpsu.edu.ph/facilities) and [CPSU states its main campus is in Camingawan](https://cpsu.edu.ph/sublink/1); the recorded caf\u00e9 pin is in the main-campus vicinity. Confirm it is the same cafeteria. No university-wide contact is presented as a cafeteria-specific number.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7783,
    "title": "Jollibee",
    "slug": "osm-node-4567931893",
    "field": "phone",
    "proposed": "(034) 471-3558",
    "notes": "Medium: [city directory](https://kabankalancity.gov.ph/tourism/resort-and-restaurants/) and [nearby-coordinate Guanzon listing](https://philippines.worldplaces.me/review/85472691-jollibee-guanzon-kabankalan-city.html) support the Guanzon branch. Confirm current; several Jollibee branches exist.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md"
  },
  {
    "id": 7656,
    "title": "Breadbox",
    "slug": "osm-node-4579156694",
    "field": "address",
    "proposed": "Guanzon Street, Kabankalan City",
    "notes": "Medium: [Wikivoyage](https://en.wikivoyage.org/wiki/Kabankalan#Q1026445) describes a Breadbox on Guanzon and the [OSM-derived map](https://hi.maps.me/maps/country-philippines/city-kabankalan-198506059/) places this Breadbox near the record pin. Confirm the branch is still there; do not assume the named building from Wikivoyage is current or transfer the address to Bread Box 7655.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_5.md"
  },
  {
    "id": 7668,
    "title": "CPSU - Coop",
    "slug": "osm-node-5328932422",
    "field": "barangay",
    "proposed": "Camingawan",
    "notes": "Medium: [CPSU](https://cpsu.edu.ph/sublink/1) places its main campus in Camingawan and [OSM's record](https://www.openstreetmap.org/node/5328932422) places the co-op in the main-campus vicinity. Verify the campus co-op's exact location and current operation. This is a campus-location inference, not a direct CPSU co-op directory entry.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_5.md"
  },
  {
    "id": 7688,
    "title": "Honda 3S Shop",
    "slug": "osm-node-4567931199",
    "field": "barangay",
    "proposed": "Barangay 3",
    "notes": "Medium: [Waze listing](https://www.waze.com/live-map/directions/ph/western-visayas/kabankalan-city/du-ek-sam,-inc.-(honda-3s-shop)?to=place.ChIJuXEYfSkRrDMRNLv7DGvCOtY) lists Du Ek Sam's Honda 3S on Guanzon in Barangay 3, near this [OSM pin](https://www.openstreetmap.org/node/4567931199). Confirm exact dealer.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_5.md"
  },
  {
    "id": 7688,
    "title": "Honda 3S Shop",
    "slug": "osm-node-4567931199",
    "field": "phone",
    "proposed": "(034) 746-7060",
    "notes": "Medium: same [Waze listing](https://www.waze.com/live-map/directions/ph/western-visayas/kabankalan-city/du-ek-sam,-inc.-(honda-3s-shop)?to=place.ChIJuXEYfSkRrDMRNLv7DGvCOtY); confirm current. Do not substitute the nearby Yamaha dealer's phone.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_5.md"
  },
  {
    "id": 7792,
    "title": "Rosalino's Chechen",
    "slug": "osm-node-6440009793",
    "field": "address",
    "proposed": "Sola Street, Kabankalan City",
    "notes": "Medium: [OSM-derived listing](https://philippines-streets.openalfa.com/kabankalan-city/eating-drinking) names Rosalino's on Sola; a [restaurant listing](https://restaurantguru.com/Rosalinos-Chicken-Inasal-and-Seafood-Kabankalan) places Rosalino's Chicken Inasal and Seafood close to the record's coordinates. Confirm the similar names identify the same business and the road is still current. Preserve the existing cover.",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_5.md"
  }
]
COLUMNS = ('place_id', 'expected_place', 'osm_slug', 'identity_status', 'field',
           'existing_value', 'proposed_value', 'comparison', 'sources_and_caveats',
           'research_document')


def safe_cell(value):
    text = str(value if value is not None else '')
    return "'" + text if text.lstrip().startswith(('=', '+', '-', '@')) else text


def comparison(field, current, proposed):
    if current == proposed:
        return 'ALREADY MATCHES - no update'
    if not current or (field == 'address' and current.strip().casefold() == 'address not independently verified'):
        return 'BLANK OR PLACEHOLDER - review before adding'
    return 'EXISTING VALUE - do not replace without explicit approval'


def build_rows(places, proposals=PROPOSALS):
    """Return review rows; mismatched IDs/slugs/titles are never candidates."""
    result = []
    for item in proposals:
        place = places.get(item['id'])
        valid = bool(place and place.city_id == 2 and place.is_active and place.is_verified
                     and place.slug == item['slug'] and place.title == item['title'])
        if valid:
            current = (place.category.name if place.category else '') if item['field'] == 'category' else getattr(place, item['field'])
            state = 'MATCHED - verify location and sources'
            comp = comparison(item['field'], current or '', item['proposed'])
            if item['field'] == 'category':
                comp = 'CATEGORY REVIEW ONLY - live category must be checked'
        else:
            current = ''
            state = 'STOP - missing or changed identity/scope'
            comp = 'NOT A CANDIDATE'
        result.append({'place_id': item['id'], 'expected_place': item['title'], 'osm_slug': item['slug'],
                       'identity_status': state, 'field': item['field'], 'existing_value': current or '',
                       'proposed_value': item['proposed'], 'comparison': comp,
                       'sources_and_caveats': item['notes'], 'research_document': item['document']})
    return result


def write_report(path, rows):
    with path.open('x', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: safe_cell(row[key]) for key in COLUMNS})


def main():
    root = Path.cwd()
    if not (root / 'manage.py').is_file():
        raise SystemExit('STOP: open PowerShell in the project folder containing manage.py.')
    sys.path.insert(0, str(root))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    import django
    django.setup()
    from django.conf import settings
    from apps.places.models import Place
    db = settings.DATABASES['default']
    if (db['ENGINE'] != 'django.db.backends.mysql' or db['NAME'] != 'exploreanywhere'
            or str(db.get('HOST', '')).lower() not in ('localhost', '127.0.0.1', '::1')):
        raise SystemExit('STOP: expected local MySQL/MariaDB exploreanywhere. No changes made.')
    ids = {p['id'] for p in PROPOSALS}
    # Only the existing proposed records and category names are read. No save/update/delete calls.
    found = Place.objects.filter(pk__in=ids).select_related('category').only(
        'id', 'city_id', 'is_active', 'is_verified', 'slug', 'title', 'address',
        'barangay', 'phone', 'email', 'website', 'category__name')
    rows = build_rows({p.pk: p for p in found})
    folder = Path.home() / 'EK_visitor_reports' / datetime.now().strftime('change_preview_%Y%m%d_%H%M%S_%f')
    folder.mkdir(parents=True, exist_ok=False)
    path = folder / 'visitor_change_preview.csv'
    write_report(path, rows)
    counts = Counter(r['comparison'] for r in rows)
    print('Research proposals:', len(rows), 'fields for', len(ids), 'places')
    for key, count in sorted(counts.items()):
        print(f'{key}: {count}')
    print('Preview:', path)
    print('READ ONLY: no database, media or project files changed.')
    print('These are review proposals, not verified facts. No field is approved by this report.')
    print('The CSV includes public place contacts. Review before sharing; formula-like cells are escaped.')


if __name__ == '__main__':
    main()
