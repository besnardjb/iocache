{
    "caches": {
        "burst" : {"bw": "1G", "size": "10G"},
        "storage" : {"bw": "500M", "size": "1T"},
        "a_localcache" : {"bw": "2G", "size": "5G"},
        "b_localcache" : {"bw": "2G", "size": "5G"},
        "c_localcache" : {"bw": "2G", "size": "5G"}

    },
    "links": {
        "a_local": {"bw":"2G", "to": "a_localcache"},
        "b_local": {"bw":"2G", "to": "b_localcache"},
        "c_local": {"bw":"2G", "to": "c_localcache"},
        "a_localcache_burst": {"bw":"1G", "from":"a_localcache", "to": "burst"},
        "b_localcache_burst": {"bw":"1G", "from":"b_localcache", "to": "burst"},
        "c_localcache_burst": {"bw":"1G", "from":"c_localcache", "to": "burst"},
        "burst_stor": {"bw":"1G", "from": "burst", "to" : "storage"}
    }
}
