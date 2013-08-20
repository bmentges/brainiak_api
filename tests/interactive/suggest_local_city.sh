curl -X POST http://localhost:5100/_range_search?do_item_count=1 -T suggest_local_city.json | python -m json.tool
