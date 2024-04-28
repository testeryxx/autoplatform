import yaml

x = {
            "context":{
                "search_key":"反派"
            },
            "steps": [{
                "command":"wait_activity",
                "target":".ui.home.MainActivity",
                "value": "10"
            },{
                "command": "click",
                "target": '//*[@resource-id="com.zhao.myreader:id/iv_search"]'
            },{
                "command": "wait_activity",
                "target": '.ui.search.SearchBookActivity',
                "value": "10"
            },{
                "command": "send_keys",
                "target": '//*[@resource-id="com.zhao.myreader:id/et_search_key"]',
                "value": '!search_key'
            },{
                "command": "click",
                "target": '//*[@resource-id="com.zhao.myreader:id/tv_search_conform"]'
            },{
                "command": "wait_implicitly",
                "value": '10'
            },{
                "command": "assert_text_contains",
                "target": '//*[@resource-id="com.zhao.myreader:id/tv_book_name"][1]',
                'value': '!search_key'
            },]
        }
wfile = open("/tmp/test_search.yaml","w+", encoding="utf-8")
yaml.dump(x, wfile,allow_unicode=True)
wfile.close()