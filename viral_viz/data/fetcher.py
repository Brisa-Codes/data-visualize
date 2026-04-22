import pandas as pd
import requests
import warnings
import time

warnings.filterwarnings('ignore')


# ─────────────────────────────────────────────────────────────────────
# BUILT-IN DATASET CATALOG
# Organized by category. Each entry has a title, description, and data.
# ─────────────────────────────────────────────────────────────────────

DATASET_CATALOG = {
    "Economy": {
        "GDP by Country (Billions USD)": {
            "description": "Gross Domestic Product of the world's largest economies.",
            "data": {
                "year": list(range(1990, 2024)),
                "USA":      [5963,6158,6520,6858,7287,7639,8073,8577,9062,9631,10252,10582,10936,11458,12213,13036,13815,14451,14712,14448,14992,15543,16197,16785,17527,18224,18715,19519,20580,21373,20893,23315,25464,26949],
                "China":    [360,383,422,444,564,734,863,961,1029,1094,1211,1339,1471,1660,1955,2285,2752,3550,4594,5101,6087,7551,8532,9570,10438,11061,11233,12310,13894,14280,14722,17734,17963,17700],
                "Japan":    [3132,3536,3853,4414,4850,5449,4710,4324,4032,4432,4887,4303,4115,4445,4815,4755,4530,4515,5037,5231,5700,6157,6203,5156,4850,4389,4923,4867,4955,5082,4975,4941,4233,4231],
                "Germany":  [1771,1868,2079,2071,2205,2591,2497,2212,2238,2198,1949,1944,2079,2506,2819,2861,2994,3440,3752,3418,3396,3749,3543,3733,3889,3357,3467,3677,3963,3861,3806,4259,4072,4429],
                "India":    [320,267,288,279,327,360,392,415,421,459,468,486,515,607,721,820,940,1216,1198,1342,1675,1823,1828,1857,2039,2103,2294,2651,2702,2835,2622,3150,3385,3732],
                "UK":       [1093,1081,1110,1061,1140,1346,1409,1539,1647,1686,1663,1641,1756,2054,2416,2543,2713,3085,2922,2410,2475,2619,2704,2786,3036,2928,2694,2666,2829,2831,2707,3131,3071,3332],
                "France":   [1269,1276,1372,1323,1396,1601,1611,1454,1503,1496,1362,1380,1491,1841,2117,2194,2319,2663,2929,2694,2642,2861,2683,2811,2852,2438,2471,2586,2790,2716,2603,2958,2782,3049],
                "Brazil":   [461,407,387,438,543,786,840,883,863,599,655,559,507,553,669,891,1107,1397,1696,1667,2208,2616,2465,2472,2456,1802,1796,2063,1917,1874,1444,1609,1920,2173],
                "Canada":   [593,610,579,577,579,604,628,652,632,676,744,736,757,892,1023,1173,1319,1468,1549,1371,1613,1793,1828,1847,1805,1556,1528,1649,1716,1741,1643,1988,2140,2117],
                "S. Korea": [270,315,350,386,456,556,597,558,374,485,562,533,609,680,765,898,1012,1122,1047,901,1094,1202,1223,1306,1411,1382,1415,1531,1720,1647,1631,1798,1665,1709],
            }
        },
        "GDP Per Capita (USD)": {
            "description": "GDP per person — shows living standard differences.",
            "data": {
                "year": list(range(2000, 2024)),
                "USA":       [36330,37134,38023,39496,41714,44115,46302,47976,48383,47100,48468,49883,51603,53107,55033,56863,57904,59928,62823,65120,63544,70219,76329,80035],
                "Switzerland":[37813,39857,43043,49448,52914,54466,57028,62233,72365,69672,74606,88002,83164,85112,86468,82118,79888,80450,82839,81994,85168,93260,92434,98767],
                "Norway":    [37472,37927,42393,49006,52964,65749,72325,84444,95279,79834,87648,100600,101564,102832,97013,74498,70460,75497,81695,75420,67176,89047,106149,87032],
                "Singapore": [23793,21439,22198,23672,27405,29870,33580,39224,39721,38577,46570,53117,54431,56029,56336,54941,55243,58248,64579,65234,59795,72795,82808,87884],
                "Australia": [20148,19560,20105,23371,30407,33983,36044,40960,49525,42772,51845,62081,67646,67792,62011,56755,49928,53800,57305,54907,51680,63529,65099,64491],
                "Germany":   [23719,23738,25209,30349,34044,34517,36448,41800,45427,41485,41532,46645,44005,46286,48024,41103,42136,44550,47993,46468,46208,51204,48756,52824],
                "Japan":     [38532,33847,32289,34808,37689,37218,35434,35275,39340,40855,44508,48168,48603,40442,38110,34524,38761,38332,39159,40256,39991,39301,33815,33950],
                "UK":        [28164,27691,29693,33684,40290,42030,44599,50566,47287,38713,39435,41430,42462,43449,46874,44972,41048,40361,42943,42747,40318,46510,45461,48913],
            }
        },
    },
    "Technology": {
        "Internet Users (Millions)": {
            "description": "Number of internet users by country — explosive growth story.",
            "data": {
                "year": list(range(2000, 2024)),
                "China":  [22,33,59,79,94,111,137,210,298,384,457,513,564,618,649,688,721,772,829,854,940,1012,1050,1092],
                "India":  [5,7,16,22,39,60,80,120,150,190,234,280,330,373,432,462,560,630,665,718,749,833,870,900],
                "USA":    [121,143,159,172,185,198,210,218,230,240,245,254,264,271,280,287,290,293,295,298,302,307,311,315],
                "Brazil": [9,14,22,32,46,68,80,80,84,88,95,100,107,120,126,128,139,149,150,153,155,165,170,175],
                "Japan":  [47,56,62,64,86,87,87,88,91,96,99,101,103,109,110,115,118,118,117,117,116,116,115,115],
                "Nigeria":[0.1,0.1,0.4,1,3,5,8,11,24,30,43,55,60,67,76,86,91,98,104,110,116,122,130,140],
                "Indonesia":[2,4,8,12,16,20,25,30,36,40,46,55,63,72,83,91,104,112,132,150,171,186,195,210],
                "Russia": [3,4,6,10,16,22,26,35,45,52,62,70,76,84,87,91,102,109,116,118,124,130,132,130],
            }
        },
        "Smartphone Users (Millions)": {
            "description": "Smartphone adoption race between major markets.",
            "data": {
                "year": list(range(2010, 2024)),
                "China":    [67,117,193,270,388,525,563,668,729,783,912,953,979,1000],
                "India":    [18,29,53,76,117,155,210,300,340,450,500,600,660,750],
                "USA":      [62,91,122,143,160,191,209,224,237,254,270,282,290,297],
                "Indonesia":[12,22,47,57,71,85,103,122,150,171,191,210,225,240],
                "Brazil":   [17,27,41,53,71,85,96,108,120,133,149,160,169,177],
                "Japan":    [10,20,30,50,56,59,63,66,79,83,88,92,96,100],
                "Nigeria":  [4,7,13,18,22,26,33,42,51,60,70,80,95,110],
                "Russia":   [11,19,34,48,60,68,74,79,84,89,100,106,108,110],
            }
        },
    },
    "Demographics": {
        "Population by Country (Millions)": {
            "description": "World's most populous nations over time.",
            "data": {
                "year": list(range(1990, 2024)),
                "China":     [1135,1150,1165,1178,1192,1204,1218,1230,1242,1253,1263,1272,1280,1288,1296,1304,1311,1318,1325,1331,1338,1344,1351,1357,1364,1371,1376,1383,1390,1393,1402,1413,1412,1410],
                "India":     [873,892,909,927,945,963,980,998,1016,1034,1053,1071,1090,1109,1127,1147,1166,1186,1206,1224,1241,1258,1275,1293,1311,1329,1347,1366,1383,1398,1408,1423,1428,1438],
                "USA":       [250,253,256,260,263,266,269,273,276,279,282,285,288,290,293,296,299,301,304,307,309,312,314,316,319,321,323,326,327,329,332,333,334,335],
                "Indonesia": [181,186,191,195,199,203,207,210,214,217,212,216,220,223,227,230,233,237,240,243,245,249,252,255,258,260,263,266,268,271,274,277,279,280],
                "Brazil":    [149,152,155,157,160,163,166,168,171,174,176,178,181,183,185,187,189,191,193,194,196,198,199,201,203,204,206,208,210,211,213,214,215,216],
                "Pakistan":  [108,111,115,118,121,125,128,132,136,139,143,147,151,155,159,163,167,172,176,180,184,188,193,197,202,207,212,217,221,225,228,231,235,240],
                "Nigeria":   [95,99,102,106,110,114,118,122,126,131,136,140,145,150,155,160,166,172,178,184,190,196,203,210,218,226,233,242,250,259,214,220,225,230],
                "Bangladesh":[104,107,110,113,116,118,121,123,126,128,131,133,135,138,140,142,144,147,149,151,153,155,157,159,160,161,163,165,166,168,169,170,171,172],
            }
        },
        "Life Expectancy (Years)": {
            "description": "How long people live, on average, in each country.",
            "data": {
                "year": list(range(2000, 2024)),
                "Japan":       [81.1,81.4,81.6,81.8,82.0,82.1,82.4,82.6,82.7,83.0,83.0,82.7,83.2,83.3,83.7,83.8,84.2,84.2,84.2,84.4,84.6,84.8,84.8,84.9],
                "Switzerland": [79.9,80.3,80.6,80.9,81.1,81.3,81.8,82.0,82.3,82.3,82.6,82.5,82.5,82.9,83.2,83.1,83.3,83.6,83.6,83.4,83.1,83.9,84.0,84.2],
                "S. Korea":    [75.9,76.5,77.0,77.6,78.0,78.6,79.2,79.6,80.1,80.6,80.8,81.2,81.4,81.7,82.2,82.1,82.4,82.7,82.7,83.3,83.5,83.7,83.7,83.8],
                "Australia":   [79.3,79.7,80.0,80.3,80.6,80.9,81.2,81.4,81.6,81.7,81.8,82.0,82.1,82.3,82.5,82.5,82.5,82.7,82.9,83.0,83.2,83.3,83.5,83.6],
                "USA":         [76.6,76.8,76.9,77.1,77.5,77.4,77.7,78.1,78.1,78.5,78.5,78.6,78.7,78.7,78.8,78.7,78.5,78.5,78.7,78.8,77.0,76.3,77.5,78.0],
                "China":       [71.4,71.7,72.0,72.3,72.6,73.0,73.4,73.7,74.1,74.5,74.8,75.2,75.5,75.8,76.0,76.3,76.5,76.7,77.0,77.3,77.1,77.8,78.0,78.2],
                "Brazil":      [70.2,70.6,70.9,71.1,71.4,71.7,72.0,72.3,72.6,73.0,73.4,73.7,74.0,74.4,74.7,75.0,75.3,75.5,75.7,75.9,72.8,73.0,75.0,75.5],
                "India":       [62.6,63.1,63.5,64.0,64.4,64.8,65.2,65.6,66.1,66.5,66.9,67.2,67.6,67.9,68.3,68.6,68.8,69.2,69.4,69.7,67.2,67.5,69.0,69.5],
                "Nigeria":     [46.1,46.2,46.5,47.0,47.7,48.4,49.2,50.0,50.9,51.7,52.3,53.0,53.4,53.8,54.3,54.5,54.7,55.0,55.2,55.4,55.0,55.5,55.8,56.0],
            }
        },
    },
    "Environment": {
        "CO2 Emissions (Million Tonnes)": {
            "description": "Carbon dioxide emissions — highly debated and shareable.",
            "data": {
                "year": list(range(2000, 2024)),
                "China":  [3405,3487,3694,4524,5288,5790,6414,6791,7040,7573,8287,9019,9312,9524,9544,9527,9606,9840,10063,10175,10668,11472,11397,11659],
                "USA":    [5869,5752,5802,5843,5916,5905,5761,5838,5656,5311,5498,5275,5121,5193,5254,5171,5146,5087,5269,5130,4457,4901,5032,4925],
                "India":  [1013,1034,1064,1102,1183,1244,1363,1489,1610,1728,1849,1919,2019,2098,2238,2316,2382,2461,2620,2616,2411,2710,2888,2978],
                "Russia": [1526,1543,1557,1605,1614,1616,1651,1672,1708,1592,1632,1691,1711,1665,1648,1627,1617,1622,1666,1679,1577,1756,1750,1700],
                "Japan":  [1236,1222,1250,1262,1273,1269,1242,1261,1224,1139,1177,1241,1260,1269,1262,1224,1206,1186,1139,1107,1030,1064,1030,1000],
                "Germany":[857,862,851,854,847,827,829,807,809,761,793,765,767,793,766,760,763,757,706,680,638,675,657,630],
                "S.Korea":[447,469,479,490,501,494,502,519,536,533,563,580,592,587,588,585,593,600,606,601,564,612,609,600],
                "Iran":   [333,349,369,399,433,456,485,513,521,541,561,568,567,569,584,565,579,594,584,614,579,622,640,650],
            }
        },
        "Renewable Energy Share (%)": {
            "description": "Percentage of energy from renewables — the clean energy race.",
            "data": {
                "year": list(range(2005, 2024)),
                "Iceland":   [72.6,73.0,74.1,75.0,75.8,77.1,77.5,78.5,80.0,82.1,84.0,85.2,85.7,86.0,86.3,83.7,85.0,86.1,86.5],
                "Norway":    [59.8,60.5,61.2,62.5,64.0,65.1,66.2,67.5,68.0,69.2,69.9,70.1,71.0,72.8,73.4,74.2,75.8,76.5,77.0],
                "Brazil":    [44.0,44.2,44.8,45.1,47.2,46.2,44.1,42.5,41.2,39.4,41.2,43.5,44.0,45.1,46.8,47.5,48.0,49.0,50.1],
                "Sweden":    [39.8,40.5,42.3,43.5,47.0,47.2,48.5,50.0,50.8,51.0,53.9,53.4,54.5,54.6,56.4,60.1,62.6,63.0,63.5],
                "Germany":   [6.7,7.8,9.1,9.2,9.9,11.6,12.5,13.6,12.4,13.8,14.6,14.8,15.5,16.5,17.4,19.3,19.2,20.4,21.0],
                "China":     [7.5,8.0,8.4,8.9,8.6,9.4,10.0,10.2,11.2,11.6,12.0,12.6,13.1,14.3,15.7,16.4,16.0,17.0,17.5],
                "USA":       [5.7,5.9,6.0,6.8,7.5,8.1,9.3,9.3,9.5,9.6,9.7,10.1,11.0,11.4,11.5,11.7,12.2,13.0,14.0],
                "India":     [4.5,4.7,4.9,5.1,5.3,5.5,5.7,5.8,6.0,6.3,6.9,7.4,8.4,9.1,9.4,9.6,10.8,11.5,12.2],
                "Japan":     [3.2,3.5,3.6,3.8,4.3,4.8,5.9,6.3,6.5,7.0,7.6,8.2,8.7,9.2,10.3,11.2,11.9,13.0,14.0],
            }
        },
    },
    "Sports": {
        "FIFA World Cup Goals by Country": {
            "description": "All-time FIFA World Cup goals scored by top nations.",
            "data": {
                "year": [1930,1934,1938,1950,1954,1958,1962,1966,1970,1974,1978,1982,1986,1990,1994,1998,2002,2006,2010,2014,2018,2022],
                "Brazil":   [15,16,25,47,59,77,89,103,119,127,137,152,162,169,178,193,211,224,237,248,256,265],
                "Germany":  [4,16,30,30,55,80,88,103,123,141,159,177,188,202,214,226,239,253,267,285,291,295],
                "Argentina":[18,18,18,18,18,20,23,24,28,32,44,57,67,74,82,90,96,107,112,122,133,139],
                "France":   [4,9,15,15,24,47,47,54,54,54,57,72,72,73,84,100,108,117,122,127,140,148],
                "Italy":    [0,12,16,24,37,50,55,60,70,76,86,94,105,115,122,130,136,147,152,158,158,158],
                "England":  [0,0,0,5,11,20,25,36,40,40,40,40,47,53,55,62,68,74,76,80,90,93],
                "Spain":    [0,4,4,4,9,9,9,9,9,9,9,21,27,33,42,51,61,70,84,96,103,110],
                "Uruguay":  [15,19,19,36,43,50,55,57,57,57,57,57,57,57,57,57,57,57,57,71,73,75],
            }
        },
        "Olympic Gold Medals (Cumulative)": {
            "description": "All-time Summer Olympic gold medal race between superpowers.",
            "data": {
                "year": [1952,1956,1960,1964,1968,1972,1976,1980,1984,1988,1992,1996,2000,2004,2008,2012,2016,2020,2024],
                "USA":    [76,108,142,178,213,246,280,280,363,399,437,478,518,554,590,636,682,715,755],
                "USSR/Russia":[71,108,151,187,218,268,317,397,397,452,452,478,502,529,553,573,593,617,640],
                "China":  [0,0,0,0,0,0,0,0,15,20,36,52,80,112,163,201,231,269,310],
                "UK":     [11,17,24,28,33,37,40,45,50,55,62,68,79,88,107,136,163,185,210],
                "Germany":[7,13,23,33,43,63,93,104,121,138,153,175,198,221,245,266,286,305,330],
                "France": [7,11,12,14,21,28,30,36,41,47,57,62,75,86,96,107,117,130,148],
                "Australia":[6,19,27,33,38,46,46,48,52,60,67,76,87,104,118,134,145,163,190],
                "Japan":  [4,8,12,28,35,48,57,57,62,66,69,72,78,84,93,100,112,145,174],
            }
        },
    },
    "Wealth": {
        "World's Richest People (Net Worth $B)": {
            "description": "Net worth of the world's richest billionaires over time — explosive growth.",
            "data": {
                "year": list(range(2010, 2025)),
                "Elon Musk":       [6.7, 6.7, 6.7, 6.7, 12, 13.2, 11.6, 20.1, 22.3, 22.3, 24.6, 151, 219, 180, 232],
                "Jeff Bezos":      [12.3, 18.1, 23.2, 25.2, 28.8, 50, 67, 72.8, 112, 131, 113, 177, 171, 114, 194],
                "Bernard Arnault": [27.5, 41, 24, 29, 34, 37.2, 34, 41.5, 72, 76, 84, 150, 158, 211, 186],
                "Bill Gates":      [53, 56, 61, 67, 76, 79.2, 75, 86, 90, 96.5, 113, 124, 129, 104, 128],
                "Mark Zuckerberg": [6.9, 17.5, 9.4, 19, 28.5, 35.7, 44.6, 56, 61, 62.3, 54.7, 97, 67, 106, 177],
                "Larry Ellison":   [28, 36, 39.5, 43, 48, 49.3, 43.6, 59.5, 58.5, 62.5, 59, 93, 106, 107, 141],
                "Warren Buffett":  [47, 39, 44, 53.5, 58.2, 60.8, 60.8, 75.6, 82.5, 82.5, 67.5, 96, 118, 106, 133],
                "Larry Page":      [15, 16.7, 20.3, 29.7, 29.2, 33.3, 35.2, 40.7, 48.8, 50.8, 67.5, 91.5, 111, 114, 156],
                "Sergey Brin":     [14.1, 16.7, 20.3, 28.8, 28.3, 32.6, 34.4, 39.8, 47.5, 49.8, 64, 89, 107, 110, 147],
                "Steve Ballmer":   [14.5, 13.7, 15.2, 20, 21.5, 22.7, 27.5, 33.6, 38.4, 41.2, 51.7, 68.7, 91.4, 80.7, 119],
            }
        },
        "Tech Billionaires (Net Worth $B)": {
            "description": "Tech founders and their wealth trajectories — the silicon gold rush.",
            "data": {
                "year": list(range(2012, 2025)),
                "Elon Musk":       [6.7, 6.7, 12, 13.2, 11.6, 20.1, 22.3, 22.3, 24.6, 151, 219, 180, 232],
                "Jeff Bezos":      [23.2, 25.2, 28.8, 50, 67, 72.8, 112, 131, 113, 177, 171, 114, 194],
                "Mark Zuckerberg": [9.4, 19, 28.5, 35.7, 44.6, 56, 61, 62.3, 54.7, 97, 67, 106, 177],
                "Larry Page":      [20.3, 29.7, 29.2, 33.3, 35.2, 40.7, 48.8, 50.8, 67.5, 91.5, 111, 114, 156],
                "Sergey Brin":     [20.3, 28.8, 28.3, 32.6, 34.4, 39.8, 47.5, 49.8, 64, 89, 107, 110, 147],
                "Jensen Huang":    [1.4, 1.5, 2.1, 3.2, 5.0, 6.0, 7.6, 3.2, 7.4, 29.8, 36, 33.4, 77],
                "Tim Cook":        [0.4, 0.6, 1.0, 1.5, 1.8, 2.0, 2.5, 3.2, 3.8, 4.5, 5.2, 5.8, 6.5],
                "Jack Dorsey":     [1.0, 2.0, 2.7, 3.2, 4.5, 5.3, 4.7, 5.6, 11.8, 12.3, 7.1, 4.7, 5.4],
            }
        },
    },
}


def get_categories():
    """Returns a list of all category names."""
    return list(DATASET_CATALOG.keys())


def get_datasets_in_category(category: str):
    """Returns a list of dataset titles in a given category."""
    return list(DATASET_CATALOG.get(category, {}).keys())


def get_dataset(category: str, title: str) -> pd.DataFrame:
    """Loads a dataset from the catalog and returns it as a DataFrame."""
    entry = DATASET_CATALOG[category][title]
    df = pd.DataFrame(entry["data"])
    df = df.set_index("year")
    return df


def get_dataset_description(category: str, title: str) -> str:
    """Returns the description for a dataset."""
    return DATASET_CATALOG[category][title]["description"]


class DataFetcher:
    """Handles fetching data from APIs, CSV files, and built-in catalog."""

    @staticmethod
    def from_csv(path) -> pd.DataFrame:
        """Load data from a CSV file path or file-like object."""
        try:
            df = pd.read_csv(path, index_col=0)
            df.index = pd.to_numeric(df.index, errors='ignore')
            return df
        except Exception as e:
            raise IOError(f"Failed to load CSV: {e}")

    @staticmethod
    def from_catalog(category: str, title: str) -> pd.DataFrame:
        """Loads a dataset directly from the built-in catalog."""
        return get_dataset(category, title)

    @staticmethod
    def from_world_bank(indicator: str, start_year: int, end_year: int, retries: int = 3) -> pd.DataFrame:
        """Fetch World Bank data using the direct JSON API."""
        url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}"
        params = {
            "date": f"{start_year}:{end_year}",
            "format": "json",
            "per_page": 10000,
        }
        last_exception = None
        for attempt in range(retries):
            try:
                resp = requests.get(url, params=params, timeout=15)
                resp.raise_for_status()
                payload = resp.json()
                if len(payload) < 2 or payload[1] is None:
                    raise ValueError("Empty response from World Bank API")
                records = payload[1]
                rows = []
                for rec in records:
                    if rec["value"] is not None:
                        rows.append({
                            "country": rec["country"]["value"],
                            "year": int(rec["date"]),
                            "value": float(rec["value"]),
                        })
                df = pd.DataFrame(rows)
                pivot_df = df.pivot_table(index="year", columns="country", values="value", aggfunc="first")
                pivot_df = pivot_df.sort_index()
                return pivot_df
            except Exception as e:
                last_exception = e
                time.sleep(2)
        raise RuntimeError(
            f"Failed to fetch data from World Bank after {retries} attempts: {last_exception}"
        )

    @staticmethod
    def from_kaggle(token: str, dataset_ref: str, filename: str = "",
                    index_col: str = "", entity_col: str = "", value_col: str = "") -> pd.DataFrame:
        """Fetch and optionally pivot a dataset from Kaggle with auto-detection."""
        import os
        import tempfile
        import zipfile

        os.environ['KAGGLE_API_TOKEN'] = token

        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            api = KaggleApi()
            api.authenticate()
        except Exception as e:
            raise RuntimeError(f"Kaggle authentication failed: {e}")

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                api.dataset_download_files(dataset_ref, path=tmpdir, unzip=True)
            except Exception as e:
                raise RuntimeError(f"Failed to download dataset {dataset_ref}: {e}")
            
            if filename:
                file_path = os.path.join(tmpdir, filename)
                if not os.path.exists(file_path):
                    for root, dirs, files in os.walk(tmpdir):
                        if filename in files:
                            file_path = os.path.join(root, filename)
                            break
            else:
                csv_files = []
                for root, dirs, files in os.walk(tmpdir):
                    for f in files:
                        if f.endswith('.csv'):
                            csv_files.append(os.path.join(root, f))
                if not csv_files:
                    raise FileNotFoundError("No CSV files found in the dataset.")
                csv_files.sort(key=os.path.getsize, reverse=True)
                file_path = csv_files[0]

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found in the downloaded dataset.")

            df = pd.read_csv(file_path)

            if not index_col:
                for col in df.columns:
                    if str(col).lower() in ['year', 'date', 'time', 'period']:
                        index_col = col
                        break
                if not index_col:
                    index_col = df.columns[0]

            if index_col not in df.columns:
                raise ValueError(f"Index column '{index_col}' not found in dataset.")

            if not entity_col and not value_col:
                str_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
                num_cols = df.select_dtypes(include=['number']).columns.tolist()
                
                if index_col in str_cols: str_cols.remove(index_col)
                if index_col in num_cols: num_cols.remove(index_col)

                if len(str_cols) >= 1 and len(num_cols) >= 1:
                    entity_col = str_cols[0]
                    for col in str_cols:
                        if any(x in str(col).lower() for x in ['country', 'name', 'entity', 'state']):
                            entity_col = col
                            break
                    
                    value_col = num_cols[0]
                    for col in num_cols:
                        if any(x in str(col).lower() for x in ['value', 'amount', 'total', 'population', 'gdp']):
                            value_col = col
                            break

            if entity_col and value_col:
                if entity_col in df.columns and value_col in df.columns:
                    df = df.pivot_table(index=index_col, columns=entity_col, values=value_col, aggfunc='first')
            else:
                df = df.set_index(index_col)

            df.index = pd.to_numeric(df.index, errors='coerce')
            df = df.dropna(subset=[df.index.name] if df.index.name else None)
            df = df.sort_index()
            return df
