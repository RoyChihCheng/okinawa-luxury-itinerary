# -*- coding: utf-8 -*-
"""沖繩 4 天 3 夜（2026/11/16 一 ～ 11/19 四）不自駕版 — 單一資料來源產生 index.html。

修改行程時只改下方 DATA 區，再執行：
    python build_site.py
然後用 Edge headless 轉 PDF（見 README）。
"""
import datetime
from urllib.parse import quote

# =====================================================================
# 共用工具
# =====================================================================

WEEKDAY_ZH = "一二三四五六日"


def wd(d):
    return WEEKDAY_ZH[d.weekday()]


def gmap(query):
    """Google Maps 地點搜尋連結。"""
    return "https://www.google.com/maps/search/?api=1&query=" + quote(query)


def gdir(origin, dest, mode="driving"):
    return ("https://www.google.com/maps/dir/?api=1&origin=" + quote(origin)
            + "&destination=" + quote(dest) + "&travelmode=" + mode)


def groute(stops):
    """整日多點路線（Google Maps /dir/A/B/C）。"""
    return "https://www.google.com/maps/dir/" + "/".join(quote(s) for s in stops) + "/"


# 交通方式徽章
MODE = {
    "taxi": ("🚕 計程車", "bg-amber-100 text-amber-900 border-amber-300"),
    "bus": ("🚌 路線巴士", "bg-emerald-100 text-emerald-900 border-emerald-300"),
    "tk02": ("🚌 TK02 ウミカジライナー", "bg-sky-100 text-sky-900 border-sky-300"),
    "rail": ("🚝 Yui Rail 單軌", "bg-rose-100 text-rose-900 border-rose-300"),
    "charter": ("🚐 包車（附司機）", "bg-violet-100 text-violet-900 border-violet-300"),
    "walk": ("🚶 步行", "bg-slate-100 text-slate-800 border-slate-300"),
    "luggage": ("🧳 行李配送", "bg-orange-100 text-orange-900 border-orange-300"),
}


def mode_badge(key, extra=""):
    label, cls = MODE[key]
    return (f'<span class="inline-flex items-center px-2 py-0.5 rounded-md border text-[11px] font-bold {cls}">'
            f'{label}{(" " + extra) if extra else ""}</span>')


# =====================================================================
# DATA：地點（名稱、地址、Google Maps 查詢字串）
# =====================================================================

P = {
    "airport": dict(name="那霸機場 國際線航廈", jp="那覇空港 国際線旅客ターミナル",
                    addr="〒901-0142 沖縄県那覇市鏡水150", q="那覇空港 国際線旅客ターミナル"),
    "okworld": dict(name="沖繩世界 文化王國・玉泉洞", jp="おきなわワールド 文化王国・玉泉洞",
                    addr="〒901-0616 沖縄県南城市玉城字前川1336", q="おきなわワールド 文化王国・玉泉洞"),
    "dmm": dict(name="DMM Kariyushi 水族館（iias 沖繩豐崎內）", jp="DMMかりゆし水族館／イーアス沖縄豊崎",
                addr="〒901-0225 沖縄県豊見城市豊崎3-35", q="DMMかりゆし水族館"),
    "senaga": dict(name="瀨長島 Umikaji Terrace", jp="瀬長島ウミカジテラス",
                   addr="〒901-0233 沖縄県豊見城市瀬長174-6", q="瀬長島ウミカジテラス"),
    "hyatt": dict(name="那霸凱悅酒店", jp="ハイアット リージェンシー 那覇 沖縄",
                  addr="〒900-0013 沖縄県那覇市牧志3-6-20（TEL 098-866-8888）", q="ハイアット リージェンシー 那覇 沖縄"),
    "kokusai": dict(name="國際通", jp="国際通り", addr="沖縄県那覇市（県庁前～安里 約 1.6 km）", q="国際通り 那覇"),
    "c_and_c": dict(name="C&C BREAKFAST OKINAWA", jp="C&C BREAKFAST OKINAWA",
                    addr="沖縄県那覇市松尾2-9-6 タカミネビル1F", q="C&C BREAKFAST OKINAWA 那覇 松尾"),
    "kyoda": dict(name="道之驛 許田（山原物產中心）", jp="道の駅 許田 やんばる物産センター",
                  addr="〒905-0024 沖縄県名護市許田17-1", q="道の駅 許田 やんばる物産センター"),
    "churaumi": dict(name="沖繩美麗海水族館", jp="沖縄美ら海水族館",
                     addr="〒905-0206 沖縄県国頭郡本部町石川424（海洋博公園內）", q="沖縄美ら海水族館"),
    "kishimoto": dict(name="岸本食堂 本店", jp="きしもと食堂 本店",
                      addr="〒905-0214 沖縄県国頭郡本部町渡久地5", q="きしもと食堂 本店 本部町"),
    "kouri": dict(name="古宇利大橋", jp="古宇利大橋", addr="沖縄県国頭郡今帰仁村古宇利（全長 1,960 m，免費通行）",
                  q="古宇利大橋"),
    "manzamo": dict(name="萬座毛", jp="万座毛", addr="〒904-0411 沖縄県国頭郡恩納村字恩納2767", q="万座毛"),
    "halekulani": dict(name="沖繩海麗客蘭尼", jp="ハレクラニ沖縄",
                       addr="〒904-0401 沖縄県国頭郡恩納村名嘉真1967-1（TEL 098-953-8600）", q="ハレクラニ沖縄"),
    "rycom": dict(name="永旺夢樂城 沖繩來客夢", jp="イオンモール沖縄ライカム",
                  addr="〒901-2306 沖縄県中頭郡北中城村字ライカム1", q="イオンモール沖縄ライカム"),
    "av": dict(name="美濱美國村", jp="美浜アメリカンビレッジ",
               addr="〒904-0115 沖縄県中頭郡北谷町字美浜9-1", q="美浜アメリカンビレッジ"),
    "parco": dict(name="SAN-A 浦添西海岸 PARCO CITY", jp="サンエー浦添西海岸 PARCO CITY",
                  addr="〒901-2123 沖縄県浦添市西洲3-1-1", q="サンエー浦添西海岸 PARCO CITY"),
    "naminoue": dict(name="波上宮", jp="波上宮", addr="〒900-0031 沖縄県那覇市若狭1-25-11", q="波上宮 那覇"),
    "makishi_market": dict(name="第一牧志公設市場", jp="第一牧志公設市場",
                           addr="〒900-0014 沖縄県那覇市松尾2-10-1", q="第一牧志公設市場"),
}

# =====================================================================
# DATA：旅程設定
# =====================================================================

TRIP_START = datetime.date(2026, 11, 16)
DATES = [TRIP_START + datetime.timedelta(days=i) for i in range(4)]
assert [wd(d) for d in DATES] == ["一", "二", "三", "四"], "日期與星期不符！"
SUNSET = {"2026-11-16": "17:40", "2026-11-17": "17:39", "2026-11-18": "17:39", "2026-11-19": "17:39"}

# =====================================================================
# DATA：餐廳（首選 + 備選1 + 備選2）
# closed: 固定公休星期（中文字），build 時自動檢查不可落在當天
# =====================================================================

FOOD = {
    "d1_lunch": dict(day=1, slot="Day 1 午餐｜沖繩世界園內（週一）", items=[
        dict(tier="首選", name="健食バイキング ちゅら島（園內自助餐）", addr="おきなわワールド園內", hours="11:00–15:00（L.O. 14:30）",
             closed="", price="大人 ¥1,980", dish="島野菜與沖繩家常菜吃到飽", rsv="免訂", q="おきなわワールド 健食バイキング ちゅら島"),
        dict(tier="備選1", name="浜辺の茶屋（海景咖啡）", addr="沖縄県南城市玉城字玉城2-1", hours="平日 08:00–18:00",
             closed="", price="～¥999", dish="海景輕食、咖啡（在園區外，需另搭計程車，車程未核實）", rsv="可訂", q="浜辺の茶屋 南城市"),
        dict(tier="備選2", name="中本鮮魚店（奧武島天婦羅）", addr="沖縄県南城市玉城字奥武9", hours="10:30–18:00（10–3 月）",
             closed="四", price="～¥999", dish="現炸鮮魚天婦羅（在園區外，需另搭計程車）", rsv="免訂", q="中本鮮魚てんぷら店 奥武島"),
    ]),
    "d1_dinner": dict(day=1, slot="Day 1 晚餐｜瀨長島 Umikaji Terrace（週一）", items=[
        dict(tier="首選", name="氾濫バーガー チムフガス", addr="豊見城市瀬長174-6 ウミカジテラス #4", hours="11:00–20:00",
             closed="", price="¥1,000–1,999", dish="醬汁滿溢的氾濫漢堡", rsv="不可訂", q="氾濫バーガー チムフガス 瀬長島"),
        dict(tier="備選1", name="海とギョウザと沖縄そば カプリシャス食堂", addr="豊見城市瀬長174-6 ウミカジテラス", hours="11:00–22:00（L.O. 21:00）",
             closed="", price="¥1,000–1,999", dish="沖繩麵、煎餃；島上營業最晚", rsv="可訂", q="カプリシャス食堂 瀬長島"),
        dict(tier="備選2", name="焼肉レストラン ROINS 久茂地国際通り店（回那霸後吃）", addr="那覇市久茂地2-6-16 リバーサイドテラス久茂地1F",
             hours="17:00–23:59", closed="", price="¥8,000–9,999", dish="沖繩縣產牛燒肉", rsv="可訂", q="焼肉レストラン ロインズ 久茂地国際通り店"),
        dict(tier="甜點", name="幸せのパンケーキ ウミカジテラス沖縄店", addr="豊見城市瀬長174-6 ウミカジテラス 32号棟",
             hours="11:00–21:00（鬆餅 L.O. 19:40）", closed="", price="¥1,000–1,999", dish="舒芙蕾鬆餅", rsv="不可訂",
             q="幸せのパンケーキ 沖縄 瀬長島"),
    ]),
    "d2_lunch": dict(day=2, slot="Day 2 午餐｜本部町（週二）", items=[
        dict(tier="首選", name="きしもと食堂 本店（岸本食堂）", addr="本部町渡久地5", hours="11:00–17:00（L.O. 16:45，賣完提早收）",
             closed="三", price="¥1,000–1,999", dish="百年木灰手打沖繩麵；只收現金", rsv="不可訂", q="きしもと食堂 本店 本部町"),
        dict(tier="備選1", name="焼肉 もとぶ牧場 本部店", addr="本部町大浜881-1", hours="午 11:30–15:00（L.O. 14:00）",
             closed="", price="午 ¥1,000–1,999", dish="本部牛燒肉午間套餐", rsv="可訂", q="焼肉もとぶ牧場 本部店"),
        dict(tier="備選2", name="百年古家 大家（うふやー）", addr="名護市中山90", hours="11:00–15:30（L.O. 15:00）",
             closed="", price="午 ¥1,000–1,999", dish="百年古民家阿古豬料理（在名護，會偏離路線）",
             rsv="可訂", q="百年古家 大家 名護"),
    ]),
    "d2_snack": dict(day=2, slot="Day 2 點心｜古宇利島（週二）", items=[
        dict(tier="首選", name="KOURI SHRIMP", addr="今帰仁村古宇利436-1", hours="11:00–16:00（內用至 15:00）",
             closed="", price="¥1,000–1,999", dish="蒜味奶油蝦", rsv="可訂", q="KOURI SHRIMP 古宇利"),
        dict(tier="備選1", name="しらさ食堂", addr="今帰仁村古宇利176", hours="10:00–17:00", closed="四",
             price="¥3,000–3,999（只收現金）", dish="古宇利海膽丼、海鮮丼", rsv="不可訂", q="しらさ食堂 古宇利"),
        dict(tier="備選2", name="古宇利海洋塔 塔內餐廳", addr="今帰仁村古宇利538", hours="11:00–18:00（L.O. 17:00）",
             closed="", price="未能核實", dish="海景飲料與輕食", rsv="未能核實", q="古宇利オーシャンタワー"),
    ]),
    "d2_dinner": dict(day=2, slot="Day 2 晚餐｜恩納・入住飯店後（週二）", items=[
        dict(tier="首選", name="ハレクラニ沖縄「KINGDOM」（飯店內牛排館）", addr="ハレクラニ沖縄 館內",
             hours="17:00–22:00（L.O. 21:00）", closed="三", price="未能核實", dish="牛排與葡萄酒；入住後不必再移動",
             rsv="需訂位 TEL 098-953-9530", q="ハレクラニ沖縄"),
        dict(tier="備選1", name="ハレクラニ沖縄「House Without A Key」（飯店內）", addr="ハレクラニ沖縄 館內",
             hours="晚餐 17:00–22:00", closed="", price="未能核實", dish="海景全日餐廳", rsv="建議訂位 TEL 098-953-9530",
             q="ハレクラニ沖縄"),
        dict(tier="備選2", name="焼肉 琉球の牛 恩納本館", addr="恩納村前兼久909-2（TEL 098-965-2233）",
             hours="16:30–23:00（L.O. 22:15），年中無休", closed="", price="¥4,000–4,999 起",
             dish="沖繩縣產和牛炭火燒肉（在萬座毛南方的前兼久，與飯店反方向，需另搭計程車往返或延長包車）",
             rsv="TableCheck 線上訂位", q="焼肉 琉球の牛 恩納本館"),
    ]),
    "d3_lunch": dict(day=3, slot="Day 3 午餐｜美濱美國村（週三）", items=[
        dict(tier="首選", name="HAN'S 美浜店", addr="北谷町美浜9-1 デポアイランドA館2F", hours="11:00–23:00（L.O. 22:00）",
             closed="", price="午 ¥1,000–1,999", dish="牛排、漢堡排", rsv="可訂", q="HAN'S 美浜店 北谷"),
        dict(tier="備選1", name="Taco Loco", addr="北谷町美浜9-2 アメリカンビレッジB棟2F", hours="11:00–16:00（L.O. 15:30）",
             closed="", price="～¥1,999", dish="墨西哥塔可", rsv="可訂", q="Taco Loco 北谷 美浜"),
        dict(tier="備選2", name="BRUAL American village", addr="北谷町美浜9-21 シーサイドビル2F", hours="10:00–21:00",
             closed="", price="午 ¥2,000–2,999", dish="海景手作漢堡", rsv="可訂", q="BRUAL American village 北谷"),
    ]),
    "d3_dinner": dict(day=3, slot="Day 3 晚餐｜那霸（週三）", items=[
        dict(tier="首選", name="鉄板焼ステーキレストラン 碧 国際通り松尾店", addr="那覇市松尾1-2-9（TEL 098-941-1129）",
             hours="晚 17:00–22:00（套餐 L.O. 20:00、牛排 L.O. 21:00）；週四、週日只營業午餐", closed="", price="晚 ¥10,000–14,999",
             dish="縣產黑毛和牛＋久米島車蝦鐵板燒", rsv="需訂位（電話／一休）", q="碧 国際通り松尾店 那覇市松尾1-2-9"),
        dict(tier="備選1", name="焼肉レストラン ロインズ 松山店", addr="那覇市松山2-10-13 沖商マンション1F",
             hours="17:00–24:00（L.O. 23:00）", closed="二", price="¥8,000–9,999", dish="縣產牛燒肉", rsv="可訂",
             q="焼肉レストラン ロインズ 松山店"),
        dict(tier="備選2", name="ステーキハウス88Jr. 浦添パルコシティ店（離開 PARCO 前吃）", addr="浦添市西洲3-1-1 PARCO CITY 2F",
             hours="09:00–22:00", closed="", price="¥1,000–1,999", dish="平價牛排套餐", rsv="不可訂",
             q="ステーキハウス88Jr. 浦添パルコシティ店"),
    ]),
    "d4_brunch": dict(day=4, slot="Day 4 早午餐｜國際通・牧志（週四）", items=[
        dict(tier="首選", name="C&C BREAKFAST OKINAWA", addr="那覇市松尾2-9-6 タカミネビル1F", hours="平日 09:00–15:00（L.O. 14:00）",
             closed="二", price="¥1,000–1,999", dish="鬆餅、沖繩早餐盤", rsv="不可訂（建議 9:00 開門就到）", q="C&C BREAKFAST OKINAWA 那覇 松尾"),
        dict(tier="備選1", name="ポーたま 牧志市場店", addr="那覇市松尾2-8-35", hours="07:00–20:00", closed="",
             price="～¥999", dish="午餐肉蛋飯糰", rsv="可訂", q="ポーたま 牧志市場店"),
        dict(tier="備選2", name="沖縄そば タイラ製麺所 国際通り店", addr="那覇市牧志2-7-21 泉川ビル1F", hours="11:00–22:00",
             closed="", price="¥1,000–1,999", dish="沖繩麵（11:00 才開，適合當午餐）", rsv="不可訂", q="タイラ製麺所 国際通り店"),
    ]),
}

# 自動檢查：餐廳不可在該日公休
for _k, _slot in FOOD.items():
    _day_wd = wd(DATES[_slot["day"] - 1])
    for _it in _slot["items"]:
        assert _day_wd not in _it["closed"], f"{_it['name']} 在 Day{_slot['day']}（週{_day_wd}）公休！"

# =====================================================================
# DATA：每日行程
# timeline: (時間, 類型, 內容)  類型 = spot / move / food / hotel
# legs: 交通段；g = (起點查詢, 終點查詢, travelmode)
# cards: 景點卡
# =====================================================================

DAYS = [
    dict(
        n=1, title="抵達那霸・南部洞窟與水族館・瀨長島夕陽",
        axis="那霸機場 ➔ 沖繩世界（南城）➔ iias 豐崎・DMM 水族館 ➔ 瀨長島 ➔ 國際通 ➔ 凱悅",
        tag="行李先寄飯店・兩手空空玩",
        hotel="那霸凱悅酒店（Hyatt Regency Naha）",
        route=["那覇空港 国際線旅客ターミナル", "おきなわワールド 文化王国・玉泉洞", "DMMかりゆし水族館", "瀬長島ウミカジテラス",
               "ハイアット リージェンシー 那覇 沖縄"],
        timeline=[
            ("11:00", "move", "抵達那霸機場國際線（航班時間未提供，此為假設）"),
            ("11:40", "move", "到大和運輸「手荷物らくちん便」櫃台寄行李到凱悅（¥1,000／件，<b>13:00 前交件、19:00 前送達</b>）"),
            ("12:00", "move", "計程車 ➔ 沖繩世界（約 30–40 分，約 ¥5,450）"),
            ("12:40", "spot", "入園（一律先走玉泉洞鐘乳石洞，約 1 小時）"),
            ("13:45", "food", "園內午餐：健食バイキング ちゅら島（L.O. 14:30）"),
            ("14:30", "spot", "Super Eisa 太鼓舞表演（約 30 分）"),
            ("15:30", "move", "計程車 ➔ iias 沖繩豐崎（約 26 分，約 ¥4,250）"),
            ("16:00", "spot", "DMM Kariyushi 水族館（約 1 小時）"),
            ("17:05", "move", "計程車 ➔ 瀨長島（約 10 分，約 ¥1,450）"),
            ("17:20", "spot", "瀨長島 Umikaji Terrace 看夕陽（日落 <b>17:40</b>）"),
            ("18:00", "food", "晚餐：氾濫バーガー（營業到 20:00）"),
            ("19:05", "move", "走到 TK02 站牌（瀨長島飯店入口道路對面），搭<b>平日 19:15</b> 班（下一班 19:45）➔「国際通り入口」站約 19:50（¥360）"),
            ("19:50", "move", "沿國際通散步約 20 分走回凱悅"),
            ("20:15", "hotel", "凱悅 Check-in，領取寄來的行李"),
        ],
        legs=[
            dict(frm="那霸機場", to="沖繩世界", mode="taxi",
                 detail="國際線 1F 計程車招呼站排班，或用 GO／DiDi／Uber 叫車。約 18 km，不塞車約 30 分。",
                 cost="約 ¥5,450（推算，不含塞車計時）",
                 alt="83 番「玉泉洞線」巴士：<b>國內線 1F 6 號站</b>，平日 12:20 發 ➔ 13:20 抵「玉泉洞前」站，¥780（現金或 OKICA，<b>不收 Suica</b>）。平日機場發車只有 12:20、13:40、14:50 三班。搭巴士 13:20 才到，午餐（L.O. 14:30）與 14:30 最後一場 Eisa 只能二選一；之後的行程時間不變。",
                 g=("那覇空港 国際線旅客ターミナル", "おきなわワールド 文化王国・玉泉洞", "driving")),
            dict(frm="沖繩世界", to="iias 沖繩豐崎（DMM 水族館）", mode="taxi",
                 detail="園區出口有計程車招呼站，也可用 App 叫車。約 14 km、26 分。兩地之間<b>沒有好轉乘的巴士</b>。",
                 cost="約 ¥4,250（推算）", alt="無合適巴士，建議計程車。",
                 g=("おきなわワールド 文化王国・玉泉洞", "DMMかりゆし水族館", "driving")),
            dict(frm="iias 豐崎", to="瀨長島", mode="taxi",
                 detail="約 4.3 km、10 分，確保 17:40 日落前抵達。",
                 cost="約 ¥1,450（推算）",
                 alt="TK02「ウミカジライナー」：「イーアス沖縄豊崎（DMMかりゆし水族館）」站 ➔「瀬長島ホテル（ウミカジテラス）」站，¥200，現金或信用卡感應，<b>不收交通 IC 卡</b>。平日 iias 發車 16:22／16:52／17:32（17:32 那班會錯過 17:40 日落；要搭巴士看日落須坐 16:52，DMM 只能逛約 50 分）。※機場直達瀨長島的 TK04 只在週六日、假日行駛，<b>週一搭不到</b>。",
                 g=("DMMかりゆし水族館", "瀬長島ウミカジテラス", "driving")),
            dict(frm="瀨長島", to="凱悅（經國際通）", mode="tk02",
                 detail="「瀬長島ホテル（ウミカジテラス）」站上車（平日 18:15／18:45／19:15／19:45 發）➔「国際通り入口」站下車，約 35 分，¥360（現金／信用卡感應）。站牌在瀨長島飯店入口道路對面，提前 10 分離開商場。下車後沿國際通往東走約 1.6 km（約 20 分）回凱悅，順便逛夜晚的國際通。",
                 cost="¥360",
                 alt="計程車直達凱悅，約 8 km，約 ¥2,550（推算）；或 TK02 到赤嶺站（¥150），轉 Yui Rail 赤嶺 ➔ 牧志（¥290），再走 7–8 分。",
                 g=("瀬長島ウミカジテラス", "ハイアット リージェンシー 那覇 沖縄", "transit")),
        ],
        cards=[
            dict(p="airport", img="naha_airport.jpg", cap="那霸機場航廈（Wikimedia Commons 實景）", time="11:00 抵達",
                 title="那霸機場：先寄行李，再輕裝出發",
                 desc="入境後先到大和運輸「手荷物らくちん便」櫃台，把大行李直接寄到凱悅（收件飯店填 Hyatt Regency Naha，並寫上入住人姓名）。下午 4 個點就不用拖行李。",
                 rows=[("🧳 行李配送", "沖繩大和運輸「手荷物らくちん便」¥1,000／件；<b>13:00 前交件 ➔ 當天 19:00 前送到本島飯店</b>。櫃台在 2F，營業 9:00–19:00，從國際線到達大廳步行約 4 分。官方說可送沖繩本島住宿設施；交件時請櫃台確認可送凱悅。"),
                       ("🔁 行李備案", "Airporter「Before U Go」（2F，15:30 前交件、19:00 前送到合作飯店，是否含凱悅未核實）；或付費寄物後晚上再回機場拿（不建議）。"),
                       ("💴 現金", "岸本食堂、市場攤位、部分巴士只收現金，建議先在機場 ATM 提領日圓。"),
                       ("📱 App", "先下載 GO／DiDi／Uber（沖繩三者都能叫計程車）與 Google Maps 離線地圖。")]),
            dict(p="okworld", img="okinawa_world_gyokusendo.jpg", cap="玉泉洞鐘乳石", time="12:40–15:30",
                 title="沖繩世界 文化王國・玉泉洞", ticket="大人 ¥2,000（入園一律從玉泉洞進）",
                 hours="09:00–17:30（最終受付 16:00）",
                 desc="入園一律先走玉泉洞（約 1 小時），出洞後在園內吃午餐，再看 14:30 Super Eisa 太鼓舞（約 30 分，全天場次 10:30／12:30／14:30，14:30 為最後一場）。看完逛琉球王國城下町。※園內「沖縄そば自慢 なんと屋」自 2026/2/13 起休業中。",
                 rows=[("⏱ 建議停留", "約 2.5–3 小時"), ("👟 提醒", "洞內潮濕、地面濕滑，穿防滑平底鞋。")],
                 food="d1_lunch"),
            dict(p="dmm", img="dmm_kariyushi.jpg", cap="DMM Kariyushi 水族館（Wikimedia Commons 實景）", time="16:00–17:00",
                 title="DMM Kariyushi 水族館＋iias 沖繩豐崎",
                 ticket="11/16 屬 Value 日，大人 ¥3,100（前一天以前網購 10% OFF）", hours="09:00–19:00（最後入館 18:00；官網另一處顯示 18:00 閉館，出發前再確認）",
                 desc="位於 iias 購物中心內的新型態水族館，以光影與互動展示為主，室內好逛，1 小時剛好。iias 商店營業到 21:00。",
                 rows=[("⏱ 建議停留", "約 1 小時"), ("💡 小技巧", "17:00 後入館有 Web 優惠票（約 ¥2,170 起）；若搭巴士遲到可改用此票。")]),
            dict(p="senaga", img="senagajima_umikaji.jpg", cap="瀨長島 Umikaji Terrace（Wikimedia Commons 實景）", time="17:20–19:05",
                 title="瀨長島 Umikaji Terrace：夕陽＋晚餐", ticket="免費入場", hours="10:00–21:00（餐飲 11:00–21:00）",
                 desc="白色階梯式商場面西，<b>11/16 日落 17:40</b>，坐在露台看夕陽與機場起降的飛機，晚餐在島上吃完再回那霸。※足湯目前暫停使用（官網 11/7 公告）。",
                 rows=[("⏱ 建議停留", "約 2 小時")], food="d1_dinner"),
            dict(p="kokusai", img="kokusai_dori.jpg", cap="國際通（Wikimedia Commons 實景）", time="19:50–20:15",
                 title="國際通夜晚散步 ➔ 凱悅 Check-in", ticket="免費", hours="開放街道，各店時間不同",
                 desc="TK02 在「国際通り入口」下車後，沿國際通一路往東逛到牧志一帶，再轉進巷內到凱悅。行李已由大和運輸送到飯店。",
                 rows=[("🏨 今晚住宿", "那霸凱悅酒店（牧志 3-6-20）")]),
        ],
    ),
    dict(
        n=2, title="北部包車一日：許田 ➔ 美麗海 ➔ 古宇利 ➔ 萬座毛夕陽",
        axis="凱悅 ➔ 沖繩自動車道 ➔ 道之驛許田 ➔ 美麗海水族館 ➔ 岸本食堂 ➔ 古宇利島 ➔ 萬座毛 ➔ 海麗客蘭尼",
        tag="10 小時包車・行李放車上",
        hotel="沖繩海麗客蘭尼（Halekulani Okinawa）",
        route=["ハイアット リージェンシー 那覇 沖縄", "道の駅 許田 やんばる物産センター", "沖縄美ら海水族館", "きしもと食堂 本店 本部町",
               "古宇利オーシャンタワー", "万座毛", "ハレクラニ沖縄"],
        timeline=[
            ("08:00", "move", "凱悅大廳上包車（行李一起上車，整天放車上）"),
            ("09:15", "spot", "道之驛 許田：買美麗海門票＋早點心（08:30 開門）"),
            ("10:35", "spot", "美麗海水族館：黑潮之海、11:30 海豚秀（オキちゃん劇場）"),
            ("13:15", "food", "午餐：岸本食堂本店（賣完就收，越早越好）"),
            ("14:35", "spot", "古宇利大橋 ➔ 先吃 KOURI SHRIMP（內用到 15:00）➔ 古宇利海洋塔 ➔ Tinu 海灘心形岩"),
            ("16:00", "move", "<b>16:00 前</b>包車南下 ➔ 萬座毛（不塞車約 1 小時）"),
            ("17:05", "spot", "萬座毛 象鼻岩看夕陽（日落 <b>17:39</b>，步道開放到日落）"),
            ("18:05", "hotel", "抵達海麗客蘭尼 Check-in，包車結束（約 10 小時）"),
            ("19:00", "food", "晚餐：飯店內 KINGDOM 牛排館（需訂位）"),
        ],
        legs=[
            dict(frm="凱悅", to="道之驛 許田", mode="charter",
                 detail="走沖繩自動車道到終點許田 IC，下交流道即到。約 65 km、65–75 分。",
                 cost="包車 10 小時：約 ¥32,200（Funliday 日文司機 5 人座）～¥41,400（中文司機）；恩納北部放人加收約 ¥2,500–3,000；高速費、停車費另計。預計 18:05 左右到飯店，可能超時一個計費單位（Funliday 每 30 分 ¥3,000）。",
                 alt="自行搭「沖縄エアポートシャトル」直達美麗海，但無法順路去古宇利，回程只能到「ハレクラニ沖縄前」站（美麗海 17:00 發 ➔ 18:01 到），會錯過萬座毛夕陽。",
                 g=("ハイアット リージェンシー 那覇 沖縄", "道の駅 許田 やんばる物産センター", "driving")),
            dict(frm="許田", to="美麗海水族館", mode="charter",
                 detail="約 29 km、47 分。請司機停「P7 北ゲート立體駐車場」（北口）。", cost="（包車內）",
                 alt="—", g=("道の駅 許田 やんばる物産センター", "沖縄美ら海水族館", "driving")),
            dict(frm="美麗海", to="岸本食堂 本店", mode="charter",
                 detail="往南回本部町渡久地，約 15 分。", cost="（包車內）",
                 alt="岸本食堂售罄 ➔ 焼肉もとぶ牧場 本部店（午餐 L.O. 14:00）",
                 g=("沖縄美ら海水族館", "きしもと食堂 本店 本部町", "driving")),
            dict(frm="岸本食堂", to="古宇利島", mode="charter",
                 detail="經屋我地島上古宇利大橋，約 30–40 分。<b>大橋上禁止停車</b>，拍照請在橋頭兩端停車場。", cost="（包車內）",
                 alt="—", g=("きしもと食堂 本店 本部町", "古宇利オーシャンタワー", "driving")),
            dict(frm="古宇利島", to="萬座毛", mode="charter",
                 detail="國道 58 號南下，約 37 km、57 分（不塞車）。<b>16:00 前一定要出發</b>（預留塞車），才趕得上 17:39 日落；步道只開到日落。", cost="（包車內）",
                 alt="—", g=("古宇利オーシャンタワー", "万座毛", "driving")),
            dict(frm="萬座毛", to="海麗客蘭尼", mode="charter",
                 detail="國道 58 號往北約 10 km、15–20 分。", cost="（包車內）",
                 alt="—", g=("万座毛", "ハレクラニ沖縄", "driving")),
        ],
        cards=[
            dict(p="kyoda", img="michinoeki_kyoda.jpg", cap="道之驛 許田（Wikimedia Commons 實景）", time="09:15–09:45",
                 title="道之驛 許田（山原物產中心）", ticket="免費", hours="08:30–19:00",
                 desc="高速公路終點許田 IC 旁的休息站，有山原特產、天婦羅與水果。館內可買美麗海水族館折扣票（第三方資料：大人約 ¥2,000，限現金；官網原價 ¥2,180）。",
                 rows=[("⏱ 建議停留", "30 分")]),
            dict(p="churaumi", img="churaumi_aquarium.jpg", cap="黑潮之海大水槽", time="10:35–13:00",
                 title="沖繩美麗海水族館", ticket="大人 ¥2,180", hours="08:30–18:30（入館截止 17:30）",
                 desc="主角是「黑潮之海」大水槽的鯨鯊與鬼蝠魟。11:30 到館外的オキちゃん劇場看海豚秀（免費，場次 10:30／11:30／13:00／15:00／17:00）。鯨鯊餵食在 15:00、17:00，本行程時間對不上，以海豚秀為主。",
                 rows=[("⏱ 建議停留", "約 2.5 小時"), ("🅿️ 停車", "P7 北ゲート立體駐車場（包車司機處理）")]),
            dict(p="kishimoto", img="kishimoto_soba.jpg", cap="沖繩麵（示意照）", time="13:15–14:00",
                 title="午餐：岸本食堂 本店", hours="11:00–17:00，<b>週三公休</b>（11/17 週二有開）",
                 desc="明治 38 年創業，木灰汁手打麵。中午常排隊，賣完就提早打烊；若已售罄，改去附近的もとぶ牧場。",
                 rows=[("💴 付款", "只收現金")], food="d2_lunch"),
            dict(p="kouri", img="kouri_bridge.jpg", cap="古宇利大橋", time="14:35–16:00",
                 title="古宇利大橋 ➔ 古宇利島", ticket="大橋免費；海洋塔大人 ¥1,000", hours="海洋塔 10:00–18:00（最終入園 17:30）",
                 desc="車行 1,960 m 跨海大橋，過橋後先到 KOURI SHRIMP 吃蒜味蝦（內用只到 15:00），再上古宇利海洋塔看全景（約 45 分），最後到島北的 Tinu 海灘看心形岩。",
                 rows=[("⏱ 建議停留", "島上合計約 1.5 小時"),
                       ("🗺️ 島上分點", f'<a class="underline text-sky-700" target="_blank" href="{gmap("古宇利オーシャンタワー")}">古宇利海洋塔</a>・'
                        f'<a class="underline text-sky-700" target="_blank" href="{gmap("ティーヌ浜 古宇利島")}">Tinu 海灘（心形岩）</a>・'
                        f'<a class="underline text-sky-700" target="_blank" href="{gmap("KOURI SHRIMP 古宇利")}">KOURI SHRIMP</a>')],
                 food="d2_snack"),
            dict(p="manzamo", img="manzamo.jpg", cap="萬座毛 象鼻岩", time="17:05–17:50",
                 title="萬座毛 象鼻岩夕陽", ticket="¥100（設施入口售票機）", hours="設施 08:00–19:00；<b>遊步道只開放到日落</b>",
                 desc="珊瑚礁斷崖形成的象鼻岩。<b>11/17 日落 17:39</b>，約 17:05 到達，可以從容走完環狀步道並拍夕陽。",
                 rows=[("⏱ 建議停留", "約 35–45 分")]),
            dict(p="halekulani", img="halekulani_okinawa.jpg", cap="飯店示意照（照片來源未核實）", time="18:05 Check-in",
                 title="入住 沖繩海麗客蘭尼＋館內晚餐",
                 desc="包車直接送到飯店大門，行李一起卸下。晚餐在館內吃，不必再移動。<b>注意：館內法式餐廳 SHIROUX 週二公休</b>；KINGDOM 週三公休，週二可訂。",
                 rows=[("📞 餐廳訂位", "098-953-9530（晚餐可提前 5 個月訂）")], food="d2_dinner"),
        ],
    ),
    dict(
        n=3, title="中部購物動線：Rycom ➔ 美國村 ➔ PARCO CITY ➔ 回那霸",
        axis="海麗客蘭尼 ➔ AEON Rycom ➔ 美濱美國村 ➔ PARCO CITY ➔ 凱悅",
        tag="8 小時包車・一路往南不折返",
        hotel="那霸凱悅酒店（Hyatt Regency Naha）",
        route=["ハレクラニ沖縄", "イオンモール沖縄ライカム", "美浜アメリカンビレッジ", "サンエー浦添西海岸 PARCO CITY",
               "ハイアット リージェンシー 那覇 沖縄"],
        timeline=[
            ("08:00", "hotel", "飯店早餐、海灘散步"),
            ("10:00", "move", "Check-out，上 8 小時包車（行李整天放車上）"),
            ("10:50", "spot", "AEON Mall 沖繩 Rycom（10:00 開門）"),
            ("12:20", "move", "包車 ➔ 美國村（約 15 分）"),
            ("12:35", "food", "午餐：HAN'S 美浜店"),
            ("13:30", "spot", "美國村 Depot Island、摩天輪、Sunset Beach 散步"),
            ("15:00", "move", "包車 ➔ PARCO CITY（約 25 分）"),
            ("15:25", "spot", "PARCO CITY 購物＋海景"),
            ("17:30", "move", "包車 ➔ 凱悅（下班尖峰約 20–40 分），包車約 18:00 結束，塞車可能超時"),
            ("18:00", "hotel", "凱悅 Check-in"),
            ("19:00", "food", "晚餐：碧 国際通り松尾店 鐵板燒（需訂位）"),
        ],
        legs=[
            dict(frm="海麗客蘭尼", to="AEON Rycom", mode="charter",
                 detail="約 36 km、46–55 分。恩納北部到 Rycom <b>沒有直達巴士</b>，帶行李又要跑 3 個點，包車最省事。",
                 cost="包車 8 小時：約 ¥27,600 起（Funliday 日文司機 5 人座），恩納北部出發加收約 ¥2,500–3,000；okitour 規定起訖在恩納最少包 8 小時。",
                 alt="全程計程車：四段合計約 ¥17,700＋高速費（推算），每站都要自己搬行李。",
                 g=("ハレクラニ沖縄", "イオンモール沖縄ライカム", "driving")),
            dict(frm="AEON Rycom", to="美國村", mode="charter",
                 detail="約 6 km、11–15 分。", cost="（包車內）",
                 alt="計程車約 ¥1,850（推算）。舊 96 番 Rycom–北谷巴士據報已停駛（未能核實官方公告），不建議搭巴士。",
                 g=("イオンモール沖縄ライカム", "美浜アメリカンビレッジ", "driving")),
            dict(frm="美國村", to="PARCO CITY", mode="charter",
                 detail="國道 58 號南下，約 10.6 km、20–25 分。", cost="（包車內）",
                 alt="43 番「北谷線」上り：「美浜アメリカンビレッジ」站 ➔「サンエーパルコシティ前」站（班距、票價未能核實）；計程車約 ¥3,250。",
                 g=("美浜アメリカンビレッジ", "サンエー浦添西海岸 PARCO CITY", "driving")),
            dict(frm="PARCO CITY", to="凱悅", mode="charter",
                 detail="約 6.8 km，不塞車約 20 分；平日傍晚尖峰可能 40 分。", cost="（包車內；塞車可能超時）",
                 alt="計程車約 ¥2,150；或付費接駁車「パルコシティシャトル」到おもろまち站（2024 年為 ¥300，非免費），轉 Yui Rail 到牧志站，再走 7–8 分。",
                 g=("サンエー浦添西海岸 PARCO CITY", "ハイアット リージェンシー 那覇 沖縄", "driving")),
        ],
        budget=("省錢版（不包車）",
                "① 飯店前「伊武部希望ヶ丘入口」站搭 <b>120 番 名護西空港線</b> ➔「美浜アメリカンビレッジ入口」站，約 65–70 分（平日早上約 30 分一班，例：7:56 發 ➔ 9:04 到；可付現金、信用卡感應或 OKICA，不收 Suica）。"
                "② 在北谷町觀光情報中心寄放行李（¥500／件，09:00–18:00）。③ 計程車往返 Rycom（單程約 ¥1,850）。④ 43 番巴士到 PARCO CITY。⑤ 計程車回凱悅（約 ¥2,150）。"
                "<b>順序變成 美國村 ➔ Rycom ➔ 美國村 ➔ PARCO，會折返一次</b>。也可改用 LuggAgent 把行李從海麗客蘭尼直送凱悅（09:00–11:00 取件，需 24–72 小時前預約，價格未能核實）。"),
        cards=[
            dict(p="rycom", img="aeon_rycom.jpg", cap="AEON Mall 沖繩 Rycom（Wikimedia Commons 實景）", time="10:50–12:20",
                 title="AEON Mall 沖繩 Rycom", ticket="免費", hours="專門店 10:00–22:00，年中無休",
                 desc="沖繩最大的購物中心之一，品牌齊全，適合買衣服、藥妝與伴手禮。行李放在包車上，可以輕鬆逛。",
                 rows=[("⏱ 建議停留", "約 1.5 小時"), ("🧾 退稅", "11/1 起改為「先付含稅價、出境時確認後退稅」，見實用百科。")]),
            dict(p="av", img="american_village.jpg", cap="美濱美國村（Wikimedia Commons 實景）", time="12:35–15:00",
                 title="美濱美國村（午餐＋散步）", ticket="免費", hours="開放街區，各店時間不同",
                 desc="美式街區、Depot Island 彩色建築、摩天輪與 Sunset Beach。先吃午餐，再沿海堤散步。",
                 rows=[("⏱ 建議停留", "約 2.5 小時")], food="d3_lunch"),
            dict(p="parco", img="parco_city.jpg", cap="PARCO CITY（Wikimedia Commons 實景）", time="15:25–17:30",
                 title="SAN-A 浦添西海岸 PARCO CITY", ticket="免費", hours="10:00–22:00",
                 desc="面海的大型購物中心，有大型超市（適合買沖繩零食伴手禮）。17:30 出發回那霸，避開最塞的時段。",
                 rows=[("⏱ 建議停留", "約 2 小時")]),
            dict(p="hyatt", img="hyatt_regency_naha.jpg", cap="那霸凱悅酒店（Wikimedia Commons 實景）", time="18:00 Check-in",
                 title="回到那霸凱悅＋鐵板燒晚餐",
                 desc="Check-in 後步行約 20 分（或計程車約 5 分）到國際通西端的「碧」吃鐵板燒。<b>碧松尾店週四只有午餐</b>，所以排在週三晚上。",
                 rows=[("🏨 今晚住宿", "那霸凱悅酒店（牧志 3-6-20）")], food="d3_dinner"),
        ],
    ),
    dict(
        n=4, title="波上宮・國際通伴手禮・賦歸",
        axis="凱悅 ➔ 早午餐 ➔ 波上宮 ➔ 國際通・第一牧志公設市場 ➔ 凱悅取行李 ➔ 那霸機場",
        tag="行李寄放飯店・輕裝收尾",
        hotel="—（返台）",
        route=["ハイアット リージェンシー 那覇 沖縄", "C&C BREAKFAST OKINAWA", "波上宮 那覇", "第一牧志公設市場",
               "ハイアット リージェンシー 那覇 沖縄", "那覇空港 国際線旅客ターミナル"],
        timeline=[
            ("08:45", "hotel", "Check-out，行李寄放凱悅禮賓台"),
            ("09:00", "food", "早午餐：C&C BREAKFAST（步行約 8 分，09:00 開門）"),
            ("10:00", "move", "計程車 ➔ 波上宮（約 10 分，約 ¥1,050）"),
            ("10:10", "spot", "波上宮參拜＋波の上海灘看懸崖神社"),
            ("11:00", "move", "步行 ➔ 國際通西端（約 1.3 km、18 分）"),
            ("11:20", "spot", "國際通伴手禮、第一牧志公設市場"),
            ("12:30", "move", "走回凱悅取行李"),
            ("12:40", "move", "計程車 ➔ 那霸機場國際線（約 20 分，約 ¥1,950）"),
            ("13:00", "move", "抵達機場：報到＋退稅出境確認（適用 15:00 以後起飛的航班）"),
        ],
        legs=[
            dict(frm="凱悅", to="C&C BREAKFAST", mode="walk",
                 detail="往國際通方向、轉進市場一帶，約 8 分。", cost="—", alt="—",
                 g=("ハイアット リージェンシー 那覇 沖縄", "C&C BREAKFAST OKINAWA", "walking")),
            dict(frm="C&C BREAKFAST", to="波上宮", mode="taxi",
                 detail="國際通上招車或 App 叫車，約 3 km、10 分。", cost="約 ¥1,050（推算）",
                 alt="TK02：「国際通り入口」站 ➔「波の上ビーチ（那覇クルーズターミナル）」站，¥240。",
                 g=("C&C BREAKFAST OKINAWA", "波上宮 那覇", "driving")),
            dict(frm="波上宮", to="國際通・公設市場", mode="walk",
                 detail="走到國際通西端約 1.3 km、18 分，再往東逛到市場一帶。", cost="—",
                 alt="計程車約 ¥650（起跳）。", g=("波上宮 那覇", "第一牧志公設市場", "walking")),
            dict(frm="凱悅", to="那霸機場國際線", mode="taxi",
                 detail="凱悅門口搭計程車直達國際線出發層，免換乘、免拖行李走天橋。約 6 km、20 分。",
                 cost="約 ¥1,950（推算）",
                 alt="Yui Rail：牧志站 ➔ 那霸空港站 ¥320，約 16–18 分（可刷 Suica、OKICA 或信用卡感應）。單軌站連到國內線 2F，再走連絡通道約 355 m 到國際線。",
                 g=("ハイアット リージェンシー 那覇 沖縄", "那覇空港 国際線旅客ターミナル", "driving")),
        ],
        cards=[
            dict(p="c_and_c", img="kokusai_dori.jpg", cap="國際通（Wikimedia Commons 實景，非店家照）", time="09:00–10:00",
                 title="早午餐：C&C BREAKFAST", hours="平日 09:00–15:00，<b>週二公休</b>（週四有開）",
                 desc="國際通旁市場區的人氣早餐店。行李先寄凱悅，吃完直接搭計程車去波上宮。",
                 rows=[], food="d4_brunch"),
            dict(p="naminoue", img="naminoue_shrine.jpg", cap="波上宮與懸崖", time="10:10–11:00",
                 title="波上宮：懸崖上的神社", ticket="免費參拜", hours="授與所 09:00–16:45",
                 desc="琉球八社之首，建在海邊珊瑚礁懸崖上。參拜後走到旁邊的波の上海灘，從沙灘或臨海道路的橋上拍神社懸崖全景。",
                 rows=[("⏱ 建議停留", "約 45 分")]),
            dict(p="makishi_market", img="kokusai_dori.jpg", cap="國際通（Wikimedia Commons 實景）", time="11:20–12:30",
                 title="國際通伴手禮＋第一牧志公設市場", ticket="免費", hours="市場 08:00–22:00（依店鋪）；11/19 週四有營業",
                 desc="最後採買：紅芋塔、黑糖、雪鹽金楚糕、泡盛等。市場 1F 是鮮魚、2F 是食堂，肚子餓可以吃碗沖繩麵再走。",
                 rows=[("🧾 退稅", "11/1 起購物先付含稅價，出境時在機場用護照辦理確認，之後由店家退稅（見實用百科）。")]),
            dict(p="airport", img="naha_airport.jpg", cap="那霸機場航廈（Wikimedia Commons 實景）", time="13:00 抵達",
                 title="那霸機場國際線：報到・退稅確認・出境",
                 desc="報到後、出境前，記得到免稅手續端末（或用 Visit Japan Web 線上手續）辦理購物的「出境確認」，才能拿回消費稅。",
                 rows=[("✈️ 航班提醒", "本日以 15:00 以後起飛規劃（13:00 到機場＝起飛前 2 小時）；航班較早時請刪減國際通時間。")]),
        ],
    ),
]

# 預約時間表（今天 11/14 週六）
BOOKINGS = [
    ("🔴 今天 11/14（六）", "Day 2、Day 3 包車（10h＋8h）",
     "KKday 需 3 天前（今天截止）；Funliday／Klook 需 48 小時前（最晚 11/15 08:00 前）；okitour、footprint 需 24 小時前。下單時寫明：Day 2 08:00 凱悅出發、恩納海麗客蘭尼放人；Day 3 10:00 海麗客蘭尼出發、那霸凱悅放人；兩天都要載行李。",
     "https://www.funliday.com/posts/okinawa-chartered-car/"),
    ("🔴 今天 11/14（六）", "Day 2 晚餐 KINGDOM（海麗客蘭尼館內）", "電話 098-953-9530；週三公休、週二有開。", "https://www.okinawa.halekulani.com/news/284/"),
    ("🔴 今天 11/14（六）", "Day 3 晚餐 碧 国際通り松尾店", "電話 098-941-1129 或一休線上訂位；週四只有午餐。", "https://restaurant.ikyu.com/124958"),
    ("🟠 出發前", "房間確認：凱悅（11/16、11/18）＋海麗客蘭尼（11/17）", "本指南未查空房，請確認已訂妥。", "https://www.okinawa.halekulani.com/"),
    ("🟠 出發前", "DMM Kariyushi 水族館 Web 票", "11/16 為 Value 日，大人 ¥3,100；前一天以前購買 10% OFF。", "https://kariyushi-aquarium.com/fee-ticket/"),
    ("🟠 出發前", "美麗海水族館門票", "官網購票，或在道之驛許田買（許田折扣票為第三方資料）。", "https://churaumi.okinawa/tc/"),
    ("🟠 出發前", "Visit Japan Web", "填寫入境與海關資料，截圖 QR Code。", "https://vjw-lp.digital.go.jp/zh-hant/"),
    ("🟢 當天辦", "Day 1 行李：大和運輸「手荷物らくちん便」", "機場櫃台 13:00 前交件，19:00 前送到凱悅；¥1,000／件。", "https://www.okinawayamato.co.jp/service/rakutin/"),
    ("🟢 選用", "Day 2 晚餐備選：琉球の牛 恩納本館", "TableCheck 線上訂位。", "https://www.tablecheck.com/shops/yakiniku-onna/reserve"),
]

SOURCES = [
    ("沖繩世界 票價／時間／表演", "https://www.gyokusendo.co.jp/okinawaworld/fee"),
    ("83 番巴士時刻（第三方整理）", "https://ayaca.tw/okinawa-bus-no-83-timetable/"),
    ("DMM 水族館 營業日曆", "https://kariyushi-aquarium.com/opening-hours/"),
    ("Umikaji Terrace 交通與營業", "https://umikajiterrace.com/accessguide"),
    ("東京巴士 TK02 運賃", "https://www.tokyobus.jp/okinawa/one-city-bus01/"),
    ("大和運輸 らくちん便", "https://www.okinawayamato.co.jp/service/rakutin/"),
    ("國立天文台 日落時間", "https://eco.mtk.nao.ac.jp/koyomi/dni/2026/s4811.html"),
    ("道之驛許田", "https://www.yanbaru-b.co.jp/"),
    ("美麗海水族館 營業時間", "https://churaumi.okinawa/guide/hour"),
    ("美麗海 黑潮之海節目", "https://churaumi.okinawa/program/aquarium/kuroshio"),
    ("古宇利海洋塔", "https://www.kouri-oceantower.com/facility.html"),
    ("萬座毛", "https://manzamo.jp"),
    ("海麗客蘭尼 餐廳公告（11/13）", "https://www.okinawa.halekulani.com/news/284/"),
    ("包車比較（Funliday）", "https://www.funliday.com/posts/okinawa-chartered-car/"),
    ("okitour 包車規則", "https://www.okitour.co.jp/cn/products/KOUEKI_taxi"),
    ("AEON Rycom 營業時間", "https://okinawarycom.aeonmall.jp/guide/hours"),
    ("PARCO CITY 設施", "https://www.parcocity.jp/facilities/"),
    ("120 番時刻（2026/10/19）", "https://www.kotsu-okinawa.org/time/20_120/up1.html"),
    ("波上宮", "https://www.naminouegu.jp/"),
    ("第一牧志公設市場", "https://www.makishi-public-market.jp/"),
    ("Yui Rail 乘車方式", "https://www.yui-rail.co.jp/howto/guide/"),
    ("巴士付款 FAQ", "https://daiichibus.co.jp/faq/"),
    ("計程車新費率", "https://www.okinawatimes.co.jp/articles/-/1908807"),
    ("日本退稅 2026/11/1 改制（税関）", "https://www.customs.go.jp/kaigairyoko/taxrefund/jpn.htm"),
    ("食べログ（各餐廳營業時間與公休）", "https://tabelog.com/okinawa/"),
]

# =====================================================================
# HTML 產生
# =====================================================================

TL_STYLE = {
    "spot": ("📍", "bg-sky-50 text-sky-800 border-sky-200"),
    "move": ("➡️", "bg-slate-50 text-slate-700 border-slate-200"),
    "food": ("🍽️", "bg-rose-50 text-rose-800 border-rose-200"),
    "hotel": ("🏨", "bg-amber-50 text-amber-900 border-amber-200"),
}


def place_link(key):
    p = P[key]
    return (f'<a href="{gmap(p["q"])}" target="_blank" class="text-sky-700 font-bold underline">'
            f'🗺️ Google Maps：{p["name"]} ↗</a>')


def render_food(key):
    slot = FOOD[key]
    tier_cls = {"首選": "bg-slate-50 border-slate-200", "備選1": "bg-amber-50/70 border-amber-200",
                "備選2": "bg-amber-50/70 border-amber-200", "甜點": "bg-pink-50/70 border-pink-200"}
    tier_badge = {"首選": "bg-sky-700 text-white", "備選1": "bg-amber-500 text-white", "備選2": "bg-amber-400 text-white",
                  "甜點": "bg-pink-500 text-white"}
    out = [f'<div class="space-y-2"><div class="text-xs font-black text-rose-700">🍽️ {slot["slot"]}：首選＋備選</div>'
           '<div class="grid grid-cols-1 lg:grid-cols-3 gap-2">']
    for it in slot["items"]:
        closed = f'；<b>週{it["closed"]}公休</b>' if it["closed"] else ""
        out.append(f'''<div class="p-3 rounded-xl border text-[11px] space-y-1 avoid-break {tier_cls[it["tier"]]}">
  <div class="flex items-center gap-1.5"><span class="px-1.5 py-0.5 rounded text-[10px] font-black {tier_badge[it["tier"]]}">{it["tier"]}</span>
  <span class="font-bold text-slate-900 text-xs">{it["name"]}</span></div>
  <div>📍 {it["addr"]}</div>
  <div>⏰ {it["hours"]}{closed}　✅ 當天有營業</div>
  <div>💴 {it["price"]}｜⭐ {it["dish"]}</div>
  <div>📞 {it["rsv"]}</div>
  <div><a href="{gmap(it["q"])}" target="_blank" class="text-sky-700 font-bold underline">🗺️ Google Maps ↗</a></div>
</div>''')
    out.append("</div></div>")
    return "\n".join(out)


def render_leg(i, leg):
    o, d, m = leg["g"]
    return f'''<div class="bg-white rounded-2xl border border-slate-200 p-4 text-xs space-y-1.5 avoid-break">
  <div class="flex flex-wrap items-center gap-2">
    <span class="w-6 h-6 inline-flex items-center justify-center rounded-full bg-slate-900 text-white font-black text-[11px]">{i}</span>
    <span class="font-black text-slate-900 text-sm">{leg["frm"]} ➔ {leg["to"]}</span>
    {mode_badge(leg["mode"])}
    <span class="px-1.5 py-0.5 rounded bg-emerald-600 text-white text-[10px] font-bold">建議</span>
  </div>
  <div>🧭 {leg["detail"]}</div>
  <div>💴 {leg["cost"]}</div>
  <div class="text-slate-500">🔁 替代：{leg["alt"]}</div>
  <div><a href="{gdir(o, d, m)}" target="_blank" class="text-sky-700 font-bold underline">🗺️ Google Maps 路線：{leg["frm"]} ➔ {leg["to"]} ↗</a></div>
</div>'''


def render_card(c):
    p = P[c["p"]]
    meta = []
    if c.get("hours"):
        meta.append(f'<div><strong>⏰ 時間：</strong>{c["hours"]}</div>')
    if c.get("ticket"):
        meta.append(f'<div><strong>🎟️ 票價：</strong>{c["ticket"]}</div>')
    rows = "".join(f'<div><strong>{k}：</strong>{v}</div>' for k, v in c.get("rows", []))
    food = render_food(c["food"]) if c.get("food") else ""
    return f'''<div class="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200 shadow-sm space-y-4 avoid-break">
  <div class="flex flex-col md:flex-row gap-5 items-start">
    <div class="w-full md:w-1/3 h-52 rounded-2xl overflow-hidden bg-slate-900 flex-shrink-0 relative">
      <img src="./images/{c["img"]}" alt="{p["name"]}" class="w-full h-full object-cover">
      <div class="absolute bottom-2 right-2 real-photo-badge px-2 py-0.5 rounded text-[10px] font-mono">📸 {c["cap"]}</div>
    </div>
    <div class="flex-1 space-y-3">
      <div class="flex flex-wrap items-center gap-2">
        <span class="text-xs font-bold text-sky-700 bg-sky-50 px-2.5 py-1 rounded-md">{c["time"]}</span>
        <h4 class="text-lg font-bold text-slate-900">{c["title"]}</h4>
      </div>
      <p class="text-xs text-slate-600 leading-relaxed">{c["desc"]}</p>
      <div class="bg-slate-50 p-3.5 rounded-2xl border border-slate-200 text-xs space-y-1.5">
        <div class="font-bold text-slate-800 pb-1 border-b border-slate-200">🧭 位置與資訊</div>
        <div><strong>🏷️ 日文名稱：</strong>{p["jp"]}</div>
        <div><strong>📍 地址：</strong>{p["addr"]}</div>
        {"".join(meta)}
        {rows}
        <div class="pt-0.5">{place_link(c["p"])}</div>
      </div>
    </div>
  </div>
  {food}
</div>'''


def render_day(day):
    date = DATES[day["n"] - 1]
    ds = date.isoformat()
    tl = "".join(
        f'<div class="flex items-start gap-2 p-2 rounded-lg border text-xs {TL_STYLE[t][1]}">'
        f'<span class="font-mono font-black w-12 flex-shrink-0">{tm}</span><span>{TL_STYLE[t][0]}</span><span>{txt}</span></div>'
        for tm, t, txt in day["timeline"])
    legs = "".join(render_leg(i + 1, leg) for i, leg in enumerate(day["legs"]))
    cards = "".join(render_card(c) for c in day["cards"])
    budget = ""
    if day.get("budget"):
        bt, bd = day["budget"]
        budget = (f'<div class="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 text-xs space-y-1 avoid-break">'
                  f'<div class="font-black text-emerald-900">💡 {bt}</div><div class="text-emerald-900 leading-relaxed">{bd}</div></div>')
    return f'''
<div class="day-card space-y-5" id="card-day{day["n"]}">
  <div class="bg-sky-900 text-white px-6 py-4 rounded-2xl flex items-center justify-between shadow-md">
    <div class="flex items-center space-x-3">
      <span class="text-xl font-black px-3 py-1 bg-sky-700 rounded-lg">DAY {day["n"]}</span>
      <div>
        <h3 class="text-lg font-bold">{date.month}/{date.day}（週{wd(date)}）{day["title"]}</h3>
        <p class="text-xs text-sky-200">路線：{day["axis"]}</p>
      </div>
    </div>
    <span class="text-xs bg-sky-800/80 px-3 py-1 rounded-full border border-sky-600 hidden sm:inline">{day["tag"]}</span>
  </div>

  <div class="day-grid grid grid-cols-1 lg:grid-cols-5 gap-5">
    <div class="tl-box lg:col-span-2 bg-white rounded-3xl border border-slate-200 p-5 space-y-2">
      <div class="flex items-center justify-between">
        <div class="font-black text-slate-900">⏱️ 當日時間軸</div>
        <div class="text-[11px] text-slate-500">日落 {SUNSET[ds]}</div>
      </div>
      {tl}
      <div class="text-xs pt-2 border-t border-slate-100"><strong>🏨 今晚住宿：</strong>{day["hotel"]}</div>
      <a href="{groute(day["route"])}" target="_blank" class="block text-center mt-2 py-2 rounded-xl bg-sky-600 hover:bg-sky-700 text-white font-bold text-xs">🗺️ 開啟 Day {day["n"]} 全日路線（Google Maps）</a>
    </div>
    <div class="lg:col-span-3 space-y-3">
      <div class="font-black text-slate-900">🚦 交通分段（依順序）</div>
      {legs}
      {budget}
    </div>
  </div>
  {cards}
</div>'''


def render_overview():
    rows = []
    for d in DAYS:
        date = DATES[d["n"] - 1]
        modes = sorted({leg["mode"] for leg in d["legs"]}, key=list(MODE).index)
        foods = [FOOD[c["food"]]["items"][0]["name"] for c in d["cards"] if c.get("food")]
        rows.append(f'''<tr class="hover:bg-slate-50/80">
  <td class="py-3 px-3 font-black text-sky-700 whitespace-nowrap">Day {d["n"]}<br><span class="text-[11px] text-slate-500">{date.month}/{date.day}（{wd(date)}）</span></td>
  <td class="py-3 px-3 font-medium text-slate-900">{d["axis"]}</td>
  <td class="py-3 px-3">{"<br>".join(mode_badge(m) for m in modes)}</td>
  <td class="py-3 px-3 text-rose-700 font-semibold">{"<br>".join(foods)}</td>
  <td class="py-3 px-3 font-bold text-slate-900">{d["hotel"]}</td>
</tr>''')
    return "".join(rows)


def render_matrix():
    rows = []
    for slot in FOOD.values():
        cells = []
        for tier in ("首選", "備選1", "備選2"):
            it = next(x for x in slot["items"] if x["tier"] == tier)
            closed = ("｜週" + it["closed"] + "休") if it["closed"] else ""
            cells.append(f'<td class="py-2.5 px-3"><a href="{gmap(it["q"])}" target="_blank" class="font-bold text-slate-900 underline decoration-sky-300">{it["name"]}</a>'
                         f'<div class="text-[10px] text-slate-500">{it["hours"]}{closed}</div></td>')
        rows.append(f'<tr class="hover:bg-slate-50"><td class="py-2.5 px-3 font-bold text-rose-700">{slot["slot"]}</td>{"".join(cells)}</tr>')
    return "".join(rows)


def render_bookings():
    return "".join(f'''<tr class="hover:bg-slate-50">
  <td class="py-3 px-3 font-bold whitespace-nowrap">{w}</td><td class="py-3 px-3 font-bold text-slate-900">{what}</td>
  <td class="py-3 px-3">{note}</td><td class="py-3 px-3 text-center"><a href="{url}" target="_blank" class="text-sky-700 font-bold underline">連結 ↗</a></td></tr>'''
                   for w, what, note, url in BOOKINGS)


def render_sources():
    return "".join(f'<li><a href="{u}" target="_blank" class="text-sky-700 underline">{t}</a></li>' for t, u in SOURCES)


def day_buttons():
    btns = ['<button onclick="filterDay(\'all\')" class="day-filter-btn px-3 py-1.5 rounded-xl bg-white text-slate-900 shadow-sm" data-day="all">全部天數</button>']
    for d in DAYS:
        n = d["n"]
        btns.append(f'<button onclick="filterDay(\'day{n}\')" class="day-filter-btn px-3 py-1.5 rounded-xl text-slate-600 hover:text-slate-900" data-day="day{n}">Day {n}</button>')
    return "\n          ".join(btns)


PDF_NAME = "【沖繩】極致奢享_深度遊行程規劃指南.pdf"
BUILD_DATE = "2026-11-14"

html = f'''<!DOCTYPE html>
<html lang="zh-TW" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>【沖繩】4天3夜 不自駕順路行程指南 2026/11/16–11/19 | Okinawa 4D3N</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Noto+Sans+TC:wght@300;400;500;700;900&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {{ theme: {{ extend: {{ fontFamily: {{ sans: ["Noto Sans TC", "Plus Jakarta Sans", "sans-serif"] }} }} }} }}
  </script>
  <style>
    @page {{ size: A4; margin: 10mm; }}
    @media print {{
      .no-print {{ display: none !important; }}
      body {{ background: white !important; font-size: 9.5pt !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
      .avoid-break {{ page-break-inside: avoid; break-inside: avoid; }}
      .day-card {{ display: block !important; break-before: page; }}
      header {{ position: static !important; }}
      a {{ text-decoration: none !important; }}
      /* A4 列印寬度 < md 斷點，強制套用桌面版版面 */
      .md\\:flex-row {{ flex-direction: row !important; }}
      .md\\:w-1\\/3 {{ width: 33.333% !important; }}
      .md\\:grid-cols-2 {{ grid-template-columns: repeat(2, minmax(0, 1fr)) !important; }}
      .sm\\:grid-cols-4 {{ grid-template-columns: repeat(4, minmax(0, 1fr)) !important; }}
      .lg\\:grid-cols-3 {{ grid-template-columns: repeat(3, minmax(0, 1fr)) !important; }}
      .lg\\:grid-cols-5 {{ grid-template-columns: repeat(5, minmax(0, 1fr)) !important; }}
      .lg\\:col-span-2 {{ grid-column: span 2 / span 2 !important; }}
      .lg\\:col-span-3 {{ grid-column: span 3 / span 3 !important; }}
      .h-52 {{ height: 10rem !important; }}
      .day-grid {{ display: block !important; }}
      .day-grid > div {{ margin-bottom: 12px; }}
      .tl-box > div {{ break-inside: avoid; }}
      #itinerary, #practical-guide {{ break-before: page; }}
      #card-day1 {{ break-before: auto !important; }}
    }}
    .real-photo-badge {{ background-color: rgba(15, 23, 42, 0.85); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }}
  </style>
</head>
<body class="bg-slate-50 text-slate-800 font-sans antialiased">

  <header class="sticky top-0 z-50 backdrop-blur-md bg-white/90 border-b border-slate-200/80 no-print">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <span class="text-2xl">🌊</span>
        <div>
          <span class="font-extrabold text-slate-900 tracking-tight text-lg">OKINAWA 4D3N</span>
          <span class="text-xs ml-2 px-2 py-0.5 bg-sky-100 text-sky-800 rounded-full font-bold">11/16–11/19 不自駕版</span>
        </div>
      </div>
      <nav class="hidden md:flex items-center space-x-6 text-sm font-medium text-slate-600">
        <a href="#overview" class="hover:text-sky-600">總覽</a>
        <a href="#transit-decoder" class="hover:text-sky-600">交通懶人包</a>
        <a href="#itinerary" class="hover:text-sky-600">每日行程</a>
        <a href="#food-matrix" class="hover:text-sky-600">餐廳備選表</a>
        <a href="#booking-directory" class="hover:text-sky-600">預約清單</a>
        <a href="#practical-guide" class="hover:text-sky-600">實用百科</a>
      </nav>
      <a href="./{PDF_NAME}" download class="inline-flex items-center px-4 py-2 text-xs font-bold rounded-xl text-white bg-gradient-to-r from-sky-600 to-blue-700">下載 PDF</a>
    </div>
  </header>

  <section class="relative bg-gradient-to-b from-slate-900 via-sky-950 to-slate-900 text-white py-14 sm:py-16 px-4 overflow-hidden">
    <div class="absolute inset-0 opacity-40 mix-blend-overlay"><img src="./images/manzamo.jpg" alt="萬座毛" class="w-full h-full object-cover"></div>
    <div class="relative max-w-5xl mx-auto text-center space-y-5">
      <div class="inline-flex flex-wrap justify-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 border border-white/20 text-xs font-semibold text-sky-200">
        <span>🇯🇵 日本沖繩</span><span>•</span><span>2026/11/16（一）– 11/19（四）</span><span>•</span><span>4 天 3 夜</span><span>•</span><span>不自駕：計程車＋巴士＋包車</span>
      </div>
      <h1 class="text-3xl sm:text-5xl font-black tracking-tight">沖繩 4 天 3 夜・12 個必去景點順路版</h1>
      <p class="text-sm text-slate-300 max-w-3xl mx-auto leading-relaxed">
        南部（第 1 天）➔ 北部（第 2 天）➔ 中部一路南下（第 3 天）➔ 那霸市區（第 4 天），不走回頭路。
        每段交通都有建議方式、替代方案、費用與 Google Maps 路線連結；每一餐都有首選＋2 家備選，並已核對當天是否公休。
      </p>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-4xl mx-auto pt-2 text-left">
        <div class="bg-white/10 rounded-2xl p-3.5 border border-white/10"><div class="text-xs text-sky-300 font-semibold">第 1、3 晚</div><div class="text-sm font-bold mt-1">Hyatt Regency Naha</div><div class="text-[11px] text-slate-300">那霸・國際通旁</div></div>
        <div class="bg-white/10 rounded-2xl p-3.5 border border-white/10"><div class="text-xs text-sky-300 font-semibold">第 2 晚</div><div class="text-sm font-bold mt-1">Halekulani Okinawa</div><div class="text-[11px] text-slate-300">恩納村・萬座毛北方約 10 km</div></div>
        <div class="bg-white/10 rounded-2xl p-3.5 border border-white/10"><div class="text-xs text-sky-300 font-semibold">交通主力</div><div class="text-sm font-bold mt-1">Day 2、Day 3 包車</div><div class="text-[11px] text-slate-300">Day 1 計程車＋巴士・Day 4 計程車＋步行</div></div>
        <div class="bg-white/10 rounded-2xl p-3.5 border border-white/10"><div class="text-xs text-sky-300 font-semibold">夕陽</div><div class="text-sm font-bold mt-1">瀨長島 17:40／萬座毛 17:39</div><div class="text-[11px] text-slate-300">國立天文台</div></div>
      </div>
      <div class="max-w-3xl mx-auto bg-amber-400/15 border border-amber-300/40 rounded-2xl p-3 text-xs text-amber-100 text-left space-y-1">
        <div>⚠️ <b>航班假設</b>：未提供航班時間，本行程以「11/16 約 11:00 抵達那霸、11/19 15:00 以後起飛」規劃；時間不同時，Day 1 前段與 Day 4 後段需調整。</div>
        <div>⚠️ <b>包車要今天（11/14）就訂</b>，見下方預約清單。</div>
      </div>
    </div>
  </section>

  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-14">

    <section id="overview" class="space-y-4">
      <div><span class="text-xs font-bold text-sky-600 uppercase tracking-widest">Overview</span>
      <h2 class="text-2xl font-black text-slate-900 mt-1">4 天行程總覽（12 個必去點全收）</h2></div>
      <div class="overflow-x-auto bg-white rounded-3xl border border-slate-200 shadow-sm">
        <table class="w-full text-left text-xs border-collapse">
          <thead><tr class="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
            <th class="py-3 px-3">日期</th><th class="py-3 px-3">路線</th><th class="py-3 px-3">交通</th><th class="py-3 px-3">首選餐廳</th><th class="py-3 px-3">住宿</th></tr></thead>
          <tbody class="divide-y divide-slate-100 text-slate-600">{render_overview()}</tbody>
        </table>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-4 text-xs grid grid-cols-2 sm:grid-cols-4 gap-2">
        <div>✅ 國際通（D1 夜、D4）</div><div>✅ 沖繩世界（D1）</div><div>✅ DMM 水族館／iias（D1）</div><div>✅ 瀨長島（D1）</div>
        <div>✅ 道之驛許田（D2）</div><div>✅ 美麗海水族館（D2）</div><div>✅ 古宇利大橋（D2）</div><div>✅ 萬座毛（D2）</div>
        <div>✅ AEON Rycom（D3）</div><div>✅ 美國村（D3）</div><div>✅ PARCO CITY（D3）</div><div>✅ 波上宮（D4）</div>
      </div>
    </section>

    <section id="transit-decoder" class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-5 avoid-break">
      <div><span class="text-xs font-bold text-sky-600 uppercase tracking-widest">Transit Cheat Sheet</span>
      <h2 class="text-2xl font-black text-slate-900 mt-1">不自駕交通懶人包</h2></div>
      <div class="flex flex-wrap gap-2">{"".join(mode_badge(k) for k in MODE)}</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs leading-relaxed">
        <div class="bg-rose-50 border border-rose-100 rounded-2xl p-4 space-y-1">
          <div class="font-black text-rose-900">🚝 Yui Rail（單軌）</div>
          <div>可刷 Suica／OKICA 等交通 IC 卡，也可用信用卡感應（Visa、Mastercard、JCB 等）。</div>
          <div>牧志 ➔ 那霸空港 ¥320；県庁前 ➔ 那霸空港 ¥290。一日券 ¥1,000、二日券 ¥1,800。</div>
        </div>
        <div class="bg-emerald-50 border border-emerald-100 rounded-2xl p-4 space-y-1">
          <div class="font-black text-emerald-900">🚌 路線巴士</div>
          <div>琉球巴士、那霸巴士<b>不能刷 Suica</b>，只收現金或 OKICA；20、95、111、117、120 番等路線可用信用卡感應。</div>
          <div>TK02「ウミカジライナー」（東京巴士）：現金或信用卡感應，不收 IC 卡。</div>
        </div>
        <div class="bg-amber-50 border border-amber-100 rounded-2xl p-4 space-y-1">
          <div class="font-black text-amber-900">🚕 計程車</div>
          <div>2026/8/24 起：起跳 ¥650（1.65 km），之後每 350 m ¥100；22:00–05:00 加 2 成。</div>
          <div>叫車 App：GO、DiDi、Uber 在那霸、北谷、恩納都能用。本指南的計程車費依里程推算，不含塞車計時與高速費。</div>
        </div>
        <div class="bg-violet-50 border border-violet-100 rounded-2xl p-4 space-y-1">
          <div class="font-black text-violet-900">🚐 包車（Day 2、Day 3）</div>
          <div>5 人座 8 小時約 ¥27,600 起、10 小時約 ¥32,200 起（Funliday 日文司機）；中文司機多約 ¥7,000–10,000。在恩納北部上下車加收約 ¥2,500–3,000。高速費、停車費、門票另計。</div>
          <div>一定要選<b>綠牌營業車</b>（合法載客）。</div>
        </div>
      </div>
    </section>

    <section id="itinerary" class="space-y-8">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div><span class="text-xs font-bold text-sky-600 uppercase tracking-widest">Day by Day</span>
        <h2 class="text-2xl font-black text-slate-900 mt-1">每日行程：時間軸＋交通分段＋景點卡</h2></div>
        <div class="flex flex-wrap gap-1.5 bg-slate-200/70 p-1.5 rounded-2xl no-print text-xs font-bold">
          {day_buttons()}
        </div>
      </div>
      {"".join(render_day(d) for d in DAYS)}
    </section>

    <section id="food-matrix" class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-4 avoid-break">
      <div><span class="text-xs font-bold text-sky-600 uppercase tracking-widest">Backup Restaurant Matrix</span>
      <h2 class="text-2xl font-black text-slate-900 mt-1">餐廳備選總表（首選＋備選1＋備選2，皆已核對當天營業）</h2></div>
      <div class="overflow-x-auto"><table class="w-full text-left text-xs border-collapse">
        <thead><tr class="bg-slate-100 text-slate-700 font-bold border-b border-slate-200"><th class="py-3 px-3">餐次</th><th class="py-3 px-3">首選</th><th class="py-3 px-3">備選 1</th><th class="py-3 px-3">備選 2</th></tr></thead>
        <tbody class="divide-y divide-slate-100 text-slate-600">{render_matrix()}</tbody>
      </table></div>
      <div class="text-[11px] text-slate-500">已排除：沖繩世界 なんと屋（2026/2/13 起休業）、山原そば（週一、週二公休）、古宇利 Shrimp Wagon（食べログ標示已歇業）、海麗客蘭尼 SHIROUX（週二公休）。</div>
    </section>

    <section id="booking-directory" class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-4 avoid-break">
      <div><span class="text-xs font-bold text-sky-600 uppercase tracking-widest">Booking Deadlines</span>
      <h2 class="text-2xl font-black text-slate-900 mt-1">行前預約時間表（以今天 11/14 週六計）</h2></div>
      <div class="overflow-x-auto"><table class="w-full text-left text-xs border-collapse">
        <thead><tr class="bg-slate-100 text-slate-700 font-bold border-b border-slate-200"><th class="py-3 px-3">何時</th><th class="py-3 px-3">項目</th><th class="py-3 px-3">說明</th><th class="py-3 px-3 text-center">連結</th></tr></thead>
        <tbody class="divide-y divide-slate-100 text-slate-600">{render_bookings()}</tbody>
      </table></div>
    </section>

    <section id="practical-guide" class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
      <div><span class="text-xs font-bold text-sky-600 uppercase tracking-widest">Practical Guide</span>
      <h2 class="text-2xl font-black text-slate-900 mt-1">行前實用百科</h2></div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs leading-relaxed">
        <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200 space-y-2 avoid-break">
          <h3 class="font-bold text-slate-900 text-sm">🧾 退稅新制（2026/11/1 起）</h3>
          <ul class="list-disc list-inside space-y-1 text-slate-600">
            <li>免稅店改收<b>含稅價</b>，不再當場免稅。</li>
            <li>出境時在那霸機場的免稅手續端末出示護照（或用 Visit Japan Web 線上手續），由海關確認商品帶出境，之後店家退還消費稅。</li>
            <li>消耗品不再需要特殊封口袋。退款方式（信用卡、App 等）依店家而定，結帳時請問清楚。</li>
          </ul>
        </div>
        <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200 space-y-2 avoid-break">
          <h3 class="font-bold text-slate-900 text-sm">🧳 行李策略（不自駕的關鍵）</h3>
          <ul class="list-disc list-inside space-y-1 text-slate-600">
            <li>Day 1：機場寄「らくちん便」到凱悅（13:00 前交件）。</li>
            <li>Day 2、Day 3：行李放包車上。</li>
            <li>Day 4：寄放凱悅禮賓台，回飯店取再搭計程車去機場（飯店寄機場的配送最快也要 15:00–16:00 才到，來不及）。</li>
          </ul>
        </div>
        <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200 space-y-2 avoid-break">
          <h3 class="font-bold text-slate-900 text-sm">🌤️ 11 月中旬天氣</h3>
          <ul class="list-disc list-inside space-y-1 text-slate-600">
            <li>那霸 11 月平均高溫約 24°C、低溫約 19°C（概略值）。白天短袖，早晚與海邊風大，帶薄外套。</li>
            <li>出發前一天請再看各景點官網或 SNS；沖繩 2026 年夏季曾多次因颱風臨時休館或封橋。</li>
          </ul>
        </div>
        <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200 space-y-2 avoid-break">
          <h3 class="font-bold text-slate-900 text-sm">⚠️ 規矩與現金</h3>
          <ul class="list-disc list-inside space-y-1 text-slate-600">
            <li>市場與老街不要邊走邊吃，在店家指定區域吃完。</li>
            <li>海邊不要踩踏或撿拾活珊瑚。</li>
            <li>岸本食堂、部分市場攤位與巴士只收現金，建議每人準備約 ¥20,000–30,000。</li>
          </ul>
        </div>
      </div>
      <div class="text-xs">
        <div class="font-bold text-slate-900 mb-1">📚 主要資料來源（查核日 {BUILD_DATE}）</div>
        <ul class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-0.5 list-disc list-inside">{render_sources()}</ul>
        <div class="text-slate-500 mt-2">「推算」＝依官方費率與道路距離估算；「未能核實」＝找不到可靠來源，以現場為準。照片標「Wikimedia Commons 實景」者為該地點實拍；標「示意」者並非該店或該飯店實拍。</div>
      </div>
    </section>

    <footer class="text-center py-8 border-t border-slate-200 text-xs text-slate-500 space-y-2 no-print">
      <a href="./{PDF_NAME}" download class="text-sky-700 font-bold hover:underline">下載完整 PDF 手冊</a>
      <p>© 2026 Okinawa 4D3N 不自駕順路版・更新於 {BUILD_DATE}</p>
    </footer>
  </main>

  <script>
    function filterDay(day) {{
      document.querySelectorAll(".day-filter-btn").forEach(btn => {{
        if (btn.getAttribute("data-day") === day) {{
          btn.classList.add("bg-white", "text-slate-900", "shadow-sm"); btn.classList.remove("text-slate-600");
        }} else {{
          btn.classList.remove("bg-white", "text-slate-900", "shadow-sm"); btn.classList.add("text-slate-600");
        }}
      }});
      document.querySelectorAll(".day-card").forEach(card => {{
        card.style.display = (day === "all" || card.id === "card-" + day) ? "block" : "none";
      }});
    }}
  </script>
</body>
</html>
'''

if __name__ == "__main__":
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html written:", len(html), "chars")
