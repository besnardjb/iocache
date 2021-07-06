{
    "caches": {
        "burst" : {"bw": "1G", "size": "20G"},
        "storage" : {"bw": "500M", "size": "1T"},
        "d_localcache" : {"bw": "2G", "size": "5G"}

    },
    "links": {
        "a_local": {"bw":"1G", "to": "burst"},
        "b_local": {"bw":"1G", "to": "burst"},
        "c_local": {"bw":"1G", "to": "burst"},
        "d_local": {"bw":"4G", "to": "d_localcache"},
        "d_localcache_burst": {"bw":"1G", "from":"d_localcache", "to": "burst"},
        "burst_stor": {"bw":"1G", "from": "burst", "to" : "storage"}
    }
}