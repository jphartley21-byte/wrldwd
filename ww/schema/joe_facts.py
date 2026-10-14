"""Hand-assembled fact cards from Joe's own material (material/travel_history.md, place_specifics.md): places, trip types and the concrete
details Joe's photos recorded. This is the SPIKE input until the UserTravelBrief adapter exists (plan P4); every detail is a real thing
seen on a real trip, not an invented anecdote. The crime/menace layer is persona and is labelled so downstream.
"""
from ..write.seed_stage import Fact

FACTS = [
    Fact("bf_honesty", "Black Forest, Germany", "Interrail, April 2019",
         "honesty drinks stalls on a waterfall trail: a carved log gateway with a payment box and drinks left out for walkers to pay for themselves", "custom",
         tags=["trail", "box", "payment", "drinks"]),
    Fact("rot_gnome", "Rotterdam", "festival weekend, June 2023",
         "a giant black bronze garden gnome standing in a brick square under plane trees, a big public sculpture", "landmark", tags=["statue", "square", "council"]),
    Fact("boom_guillotine", "Boomtown, South Downs", "camping festival, every August",
         "a wooden guillotine prop and hand-lettered posters reading WANTED FOR EXCESSIVE ENERGY, with a free-tattoo tent and wristbands", "custom",
         tags=["festival", "wristband", "poster", "tent"]),
    Fact("ams_cola", "Amsterdam-Noord", "stopover, July 2023",
         "a windowsill line-up of eight novelty cola cans (coconut, coffee, sweet flavours) next to a bottle of rum, seen near a campsite", "custom",
         tags=["cans", "windowsill", "rum", "campsite"]),
    Fact("moto_ferry", "Bilbao to Portsmouth", "motorbike camping tour, May-June 2023",
         "riding a motorbike through France, Spain and Portugal and coming home on the Brittany Ferries crossing from northern Spain to Portsmouth", "custom",
         tags=["ferry", "bike", "lane", "crossing"]),
    Fact("interrail_pass", "Zurich to Munich", "Interrail, April 2019",
         "twelve stops in four weeks on one rail pass, validated each travel day, with a walk planned in every country", "number",
         tags=["pass", "validated", "twelve", "stops", "walk"]),
    Fact("bergen_shoes", "Bergen, Norway", "Christmas with the partner's family, 2023-2025",
         "taking shoes off at the door of the in-laws' house, three Decembers running, and a Norwegian wedding the year before", "custom",
         tags=["family", "door", "shoes", "december"]),
    Fact("marrakesh_souk", "Marrakesh", "city break, March 2025",
         "haggling in the souk, mint tea offered at every stall, being told the price is a special price just for you", "price",
         tags=["haggle", "price", "tea", "stall"]),
    # --- added 13 Oct 2026: the party / adventure / fun events the story seeds now rest on (all real, material/travel_history.md + place_specifics.md)
    Fact("rl_rotterdam", "Rotterdam", "Rolling Loud at Ahoy, 30 Jun 2023", "lime-green wristbands behind metal barriers, raised phones, a blue-arched stage, then the giant black bronze garden gnome in a brick square", "festival", tags=["wristband", "barrier", "gnome", "stage"]),
    Fact("boomtown_all", "Boomtown, South Downs", "every August 2019-2025", "wet in 2019 (tents down), dusty in 2022, a wooden guillotine prop and WANTED FOR EXCESSIVE ENERGY posters in 2024, bone dry in 2025; a pink top hat in the crowd", "festival", tags=["tent", "poster", "dust", "hat"]),
    Fact("kings_day", "Amsterdam", "King's Day, 27-28 Apr 2019", "the whole city in orange, truffles and the Avengers finale in an old red-velvet cinema, passed out briefly in the aisle", "party", tags=["orange", "cinema", "aisle", "truffles"]),
    Fact("k_gari", "K'gari (Fraser Island)", "Australia, April 2017", "a 4WD up the beach at low tide, the tide times the only rule", "adventure", tags=["4wd", "tide", "beach"]),
    Fact("lauterbrunnen", "Lauterbrunnen, Switzerland", "Interrail, 5 Apr 2019", "a valley of 72 waterfalls in deep snow; a hiking boot with red laces sinking knee-deep", "adventure", tags=["snow", "boot", "waterfalls", "72"]),
    Fact("naples_stag", "Naples and Pompeii", "stag weekend, 19-21 Mar 2026", "three-euro blue cocktails with black straws in a stone alley, a Maradona wall shrine, Vesuvius over Pompeii in March sun", "party", tags=["cocktail", "shrine", "ruins"]),
    Fact("bilbao_end", "Bilbao", "end of the motorbike tour, 10 Jun 2023", "the giant bronze spider under a green bridge, the Guggenheim's flower dog, then the ferry home to Portsmouth", "travel", tags=["spider", "ferry", "bike"]),
]
