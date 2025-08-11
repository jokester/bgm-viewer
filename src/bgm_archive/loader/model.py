from enum import Enum, IntEnum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator
from .normalizer import launder_date

_config = ConfigDict(use_enum_values=True,
                     str_strip_whitespace=True, extra="forbid")


class SubjectType(IntEnum):
    """Subject types in Bangumi."""

    BOOK = 1  # 书籍
    ANIME = 2  # 动画
    MUSIC = 3  # 音乐
    GAME = 4  # 游戏
    REAL = 6  # 三次元


class PersonType(IntEnum):
    """Person types in Bangumi."""

    OTHER = 0  # 其他

    INDIVIDUAL = 1  # 个人
    COMPANY = 2  # 公司
    ASSOCIATION = 3  # 组合


class CharacterRole(IntEnum):
    """Character role types in Bangumi."""

    MAIN = 1  # 主角
    SUPPORTING = 2  # 配角
    GUEST = 3  # 客串

    OTHER = 4  # 其他


class EpisodeType(IntEnum):
    """Episode types in Bangumi."""

    MAIN = 0  # 正篇
    SPECIAL = 1  # 特别篇
    OP = 2  # OP
    ED = 3  # ED
    TRAILER = 4  # 预告/宣传/广告
    MAD = 5  # MAD
    OTHER = 6  # 其他


class SubjectRelationType(IntEnum):
    """Relation types between subjects."""

    # Anime relations (1-99)
    ADAPTATION = 1  # Shared by Anime, Book, Game - Adaptation / 改编
    PREQUEL = 2  # Prequel / 前传
    SEQUEL = 3  # Sequel / 续集
    SUMMARY = 4  # Summary / 总集篇
    FULL_STORY = 5  # Full Story / 全集
    SIDE_STORY = 6  # Side Story / 番外篇
    CHARACTER = 7  # Character / 角色出演
    SAME_SETTING = 8  # Same setting / 相同世界观
    ALTERNATIVE_SETTING = 9  # Alternative setting / 不同世界观
    ALTERNATIVE_VERSION = 10  # Alternative version / 不同演绎
    SPIN_OFF = 11  # Spin-off / 衍生
    PARENT_STORY = 12  # Parent Story / 主线故事
    COLLABORATION = 14  # Collaboration / 联动
    OTHER = 99  # Other / 其他

    # Book relations (1000-1099)
    BOOK_SERIES = 1002  # Series / 系列
    BOOK_OFFPRINT = 1003  # Offprint / 单行本
    BOOK_ALBUM = 1004  # Album / 画集
    BOOK_PREQUEL = 1005  # Prequel / 前传
    BOOK_SEQUEL = 1006  # Sequel / 续集
    BOOK_SIDE_STORY = 1007  # Side Story / 番外篇
    BOOK_PARENT_STORY = 1008  # Parent Story / 主线故事
    BOOK_VERSION = 1010  # Version / 不同版本
    BOOK_CHARACTER = 1011  # Character / 角色出演
    BOOK_SAME_SETTING = 1012  # Same setting / 相同世界观
    BOOK_ALTERNATIVE_SETTING = 1013  # Alternative setting / 不同世界观
    BOOK_COLLABORATION = 1014  # Collaboration / 联动
    BOOK_ALTERNATIVE_VERSION = 1015  # Alternative version / 不同演绎
    BOOK_OTHER = 1099  # Other / 其他

    # Music relations (3000-3099)
    MUSIC_OST = 3001  # OST / 原声集
    MUSIC_CHARACTER_SONG = 3002  # Character Song / 角色歌
    MUSIC_OPENING_SONG = 3003  # Opening Song / 片头曲
    MUSIC_ENDING_SONG = 3004  # Ending Song / 片尾曲
    MUSIC_INSERT_SONG = 3005  # Insert Song / 插入歌
    MUSIC_IMAGE_SONG = 3006  # Image Song / 印象曲
    MUSIC_DRAMA = 3007  # Drama / 广播剧
    MUSIC_OTHER = 3099  # Other / 其他

    # Game relations (4000-4099)
    GAME_PREQUEL = 4002  # Prequel / 前传
    GAME_SEQUEL = 4003  # Sequel / 续集
    GAME_SIDE_STORY = 4006  # Side Story / 外传
    GAME_CHARACTER = 4007  # Character / 角色出演
    GAME_SAME_SETTING = 4008  # Same Setting / 相同世界观
    GAME_ALTERNATIVE_SETTING = 4009  # Alternative Setting / 不同世界观
    GAME_ALTERNATIVE_VERSION = 4010  # Alternative Version / 不同演绎
    # GAME_VERSION = 4011  # Version / 不同版本
    GAME_PARENT_STORY = 4012  # Parent Story / 主线故事
    # GAME_MAIN_VERSION = 4013  # Main Version / 主版本
    GAME_COLLABORATION = 4014  # Collaboration / 联动
    GAME_DLC = 4015  # DLC / 扩展包
    GAME_VERSION = 4016  # Version / 不同版本
    GAME_MAIN_VERSION = 4017  # Main Version / 主版本
    GAME_COLLECTION = 4018  # Collection / 合集
    GAME_IN_COLLECTION = 4019  # In Collection / 收录作品
    GAME_OTHER = 4099  # Other / 其他


class CharacterSubjectType(IntEnum):
    """Character types in subject-character relationships."""

    MAIN = 1  # 主角
    SUPPORTING = 2  # 配角
    GUEST = 3  # 客串


class PlatformType(IntEnum):
    """Platform types for different subject types."""

    # Common platforms
    NONE = 0  # 其他

    # Book platforms (1000-1099)
    BOOK_COMIC = 1001  # 漫画
    BOOK_NOVEL = 1002  # 小说
    BOOK_ILLUSTRATION = 1003  # 画集
    BOOK_PICTURE = 1004  # 绘本
    BOOK_PHOTO = 1005  # 写真
    BOOK_OFFICIAL = 1006  # 公式书

    # Anime platforms (1-99)
    ANIME_TV = 1  # TV
    ANIME_OVA = 2  # OVA
    ANIME_MOVIE = 3  # 剧场版
    ANIME_SHORT_FILM = 4  # 短片
    ANIME_WEB = 5  # WEB
    ANIME_COMIC = 2006  # 动态漫画

    # Music platforms (3000-3099)
    MUSIC_ALBUM = 3001  # 专辑
    MUSIC_DRAMA = 3002  # 广播剧
    MUSIC_AUDIO = 3003  # 音声
    MUSIC_RADIO = 3004  # 电台

    # Game platforms (4000-4099)
    GAME_GAMES = 4001  # 游戏
    GAME_SOFTWARE = 4002  # 软件
    GAME_DLC = 4003  # 扩展包
    GAME_DEMO = 4004  # 试玩版
    GAME_TABLE = 4005  # 桌游

    # Real/TV platforms (6000-6099)
    REAL_TV = 6001  # 电视剧
    REAL_MOVIE = 6002  # 电影
    REAL_LIVE = 6003  # 演出
    REAL_SHOW = 6004  # 综艺

    # Real regions (1-10)
    REAL_JP = 1  # 日剧
    REAL_EN = 2  # 欧美剧
    REAL_CN = 3  # 华语剧


class GamePlatform(IntEnum):
    """Game hardware platforms."""

    PC = 4  # PC
    NDS = 5  # NDS
    PSP = 6  # PSP
    PS2 = 7  # PS2
    PS3 = 8  # PS3
    XBOX360 = 9  # Xbox360
    WII = 10  # Wii
    IOS = 11  # iOS
    ARC = 12  # 街机
    XBOX = 15  # XBOX
    GAMECUBE = 17  # GameCube
    NEOGEO_POCKET_COLOR = 18  # NEOGEO Pocket Color
    SFC = 19  # SFC
    FC = 20  # FC
    NINTENDO_64 = 21  # Nintendo 64
    GBA = 22  # GBA
    GB = 23  # GB
    VIRTUAL_BOY = 25  # Virtual Boy
    WONDERSWAN_COLOR = 26  # WonderSwan Color
    DREAMCAST = 27  # Dreamcast
    PLAYSTATION = 28  # PlayStation
    WONDERSWAN = 29  # WonderSwan
    PSVITA = 30  # PS Vita
    NINTENDO_3DS = 31  # 3DS
    ANDROID = 32  # Android
    MAC_OS = 33  # Mac OS
    PS4 = 34  # PS4
    XBOX_ONE = 35  # Xbox One
    NINTENDO_SWITCH = 36  # Nintendo Switch
    WII_U = 37  # Wii U
    PS5 = 38  # PS5
    XBOX_SERIES_XS = 39  # Xbox Series X/S


class SubjectPersonType:
    class AnimeStuff(IntEnum):
        ORIGINAL_CREATOR = 1  # Original Creator / Original Work / 原作
        CHIEF_DIRECTOR = 74  # 総監督 / Chief Director / 总导演
        DIRECTOR = 2  # 監督 シリーズ監督 / Director/Direction / 导演
        ASSISTANT_DIRECTOR = 72  # 助監督 / 監督補佐 / Assistant Director / 副导演
        SCRIPT = 3  # シナリオ / Script/Screenplay / 脚本
        STORYBOARD = (
            4  # コンテ  ストーリーボード  画コンテ  絵コンテ / Storyboard / 分镜
        )
        CHIEF_EPISODE_DIRECTION = 89  # チーフ演出 / Chief Episode Direction / 主演出
        EPISODE_DIRECTION = 5  # Episode Direction / 演出
        ASSISTANT_EPISODE_DIRECTION = (
            91  # 演出助手 演出補佐 演出協力 / Assistant Episode Direction / 演出助理
        )
        MUSIC = 6  # 楽曲  音楽 / Music / 音乐
        ORIGINAL_CHARACTER_DESIGN = (
            7  # キャラ原案 / Original Character Design / 人物原案
        )
        CHARACTER_DESIGN = 8  # キャラ設定 / Character Design / 人物设定
        LAYOUT = 9  # レイアウト / Layout / 构图
        SERIES_COMPOSITION = 10  # シナリオディレクター  構成  シリーズ構成  脚本構成 / Series Composition / 系列构成
        ART_DIRECTION = (
            11  # 美術監督 アートディレクション 背景監督 / Art Direction / 美术监督
        )
        ART_DESIGN = 71  # 美術設定 / Art Design / 美术设计
        COLOR_DESIGN = 13  # 色彩設定 / Color Design / 色彩设计
        MECHANICAL_DESIGN = 16  # メカニック設定 / Mechanical Design / 机械设定
        PROP_DESIGN = 19  # プロップデザイン / Prop Design / 道具设计
        CHIEF_ANIMATION_DIRECTOR = (
            14  # チーフ作画監督 / Chief Animation Director / 总作画监督
        )
        ANIMATION_DIRECTION = (
            15  # 作監 アニメーション演出 / Animation Direction / 作画监督
        )
        ASSISTANT_ANIMATION_DIRECTION = (
            90  # 作画監督補佐 / Assistant Animation Direction / 作画监督助理
        )
        MECHANICAL_ANIMATION_DIRECTION = (
            70  # メカニック作監 / Mechanical Animation Direction / 机械作画监督
        )
        ACTION_ANIMATION_DIRECTION = (
            77  # アクション作画監督 / Action Animation Direction / 动作作画监督
        )
        DIRECTOR_OF_PHOTOGRAPHY = 17  # 撮影監督 / Director of Photography / 摄影监督
        CG_DIRECTOR = 69  # CG 監督 / CG Director / CG 导演
        THREE_DCG_DIRECTOR = 86  # 3DCG 監督 / 3DCG Director / 3DCG 导演
        SUPERVISION = (
            18  # シリーズ監修 スーパーバイザー / Supervision/Supervisor / 监修
        )
        KEY_ANIMATION = 20  # 作画 原画 / Key Animation / 原画
        SECOND_KEY_ANIMATION = 21  # 原画協力 / 2nd Key Animation / 第二原画
        MAIN_ANIMATOR = 92  # メインアニメーター / Main Animator / 主动画师
        ANIMATION_CHECK = 22  # 動画チェック / Animation Check / 动画检查
        ANIMATION_WORK = 67  # アニメーション制作 アニメ制作 アニメーション / Animation Work / 动画制作
        OP_ED = 73  # OP・ED 分鏡 / OP ED / OP・ED 分镜
        PHOTOGRAPHY = 82  # 撮影 / Photography / 摄影
        MUSIC_WORK = 65  # 楽曲制作 音楽制作 / Music Work / 音乐制作
        MUSIC_PRODUCER = 85  # 音楽プロデューサー / Music Producer / 音乐制作人
        MUSIC_ASSISTANT = 55  # 音楽アシスタント / Music Assistant / 音乐助理
        ASSOCIATE_PRODUCER = (
            24  # 製作補佐 アソシエイトプロデューサー / Associate Producer / 制作助理
        )
        BACKGROUND_ART = 25  # 背景 / Background Art / 背景美术
        COLOR_SETTING = 26  # Color Setting / 色彩指定
        DIGITAL_PAINT = 27  # Digital Paint / 数码绘图
        THREE_DCG = 75  # 3DCG / 3DCG
        PRODUCTION_MANAGER = (
            37  # 制作マネージャー 制作担当 制作班長 / Production Manager / 制作管理
        )
        EDITING = 28  # 編集 / Editing / 剪辑
        ORIGINAL_PLAN = 29  # Original Plan / 原案
        THEME_SONG_ARRANGEMENT = 30  # Theme Song Arrangement / 主题歌编曲
        THEME_SONG_COMPOSITION = 31  # Theme Song Composition / 主题歌作曲
        THEME_SONG_LYRICS = 32  # Theme Song Lyrics / 主题歌作词
        THEME_SONG_PERFORMANCE = 33  # Theme Song Performance / 主题歌演出
        INSERTED_SONG_PERFORMANCE = 34  # Inserted Song Performance / 插入歌演出
        PLANNING = 35  # プランニング  企画開発 / Planning / 企画
        PLANNING_PRODUCER = 36  # 企画プロデューサー 企画営業プロデューサー / Planning Producer / 企划制作人
        PUBLICITY = (
            38  # パブリシティ  宣伝  広告宣伝  番組宣伝  製作宣伝 / Publicity / 宣传
        )
        RECORDING = 39  # 録音 / Recording / 录音
        RECORDING_ASSISTANT = (
            40  # 録音アシスタント  録音助手 / Recording Assistant / 录音助理
        )
        SERIES_PRODUCTION_DIRECTOR = 41  # Series Production Director / 系列监督
        PRODUCTION_1 = 42  # Production / 製作
        PRODUCTION_2 = 63  # 製作 製作スタジオ / Production / 制作
        SETTING_1 = 43  # 設定 / Setting / 设定
        DESIGN_MANAGER = 84  # 設定制作 制作設定 / Design Manager / 设定制作
        SOUND_DIRECTOR = 44  # Sound Director / 音响监督
        SOUND = 45  # 音響 音声 / Sound / 音响
        SOUND_EFFECTS = 46  # 音響効果 / Sound Effects / 音效
        # エフェクト作画監督 / Special Effects Animation Direction / 特效作画监督
        SPECIAL_EFFECTS_ANIMATION_DIRECTION = 88
        SPECIAL_EFFECTS = 47  # 視覚効果 / Special Effects / 特效
        ADR_DIRECTOR = 48  # ADR Director / 配音监督
        CO_DIRECTOR = 49  # Co-Director / 联合导演
        SETTING_2 = 50  # 基本設定  場面設定  場面設計  設定 / Setting / 背景设定
        IN_BETWEEN_ANIMATION = 51  # 動画 / In-Between Animation / 补间动画
        CHIEF_PRODUCER = 58  # チーフプロデューサー チーフ制作 総合プロデューサー / Chief Producer / 总制片人
        CO_PRODUCER = 59  # Co-Producer / 联合制片人
        PRODUCER = 54  # プロデュース  プロデューサー / Producer / 制片人
        EXECUTIVE_PRODUCER = 52  # 製作総指揮 / Executive Producer / 执行制片人
        ASSISTANT_PRODUCER_1 = 53  # 協力プロデューサー  アシスタントプロデューサー / Assistant Producer / 助理制片人
        ASSISTANT_PRODUCER_2 = (
            23  # 協力プロデューサー（⚠️ 待合并） / Assistant Producer / 助理制片人
        )
        ANIMATION_PRODUCER = 87  # アニメプロデューサー  アニメーションプロデューサー / Animation Producer / 动画制片人
        SUPERVISING_PRODUCER = 80  # Supervising Producer / 监制
        ASSISTANT_PRODUCTION_MANAGER = (
            56  # 制作進行 / Assistant Production Manager / 制作进行
        )
        ASSISTANT_PRODUCTION_MANAGER_ASSISTANCE = (
            83  # 制作進行協力 / Assistant Production Manager Assistance / 制作进行协力
        )
        CASTING_DIRECTOR = (
            57  # キャスティングコーディネーター監督 / Casting Director / 演员监督
        )
        DIALOGUE_EDITING = 60  # 台詞編集 / Dialogue Editing / 台词编辑
        POST_PRODUCTION_ASSISTANT = (
            61  # ポストプロダクション協力 / Post-Production Assistant / 后期制片协调
        )
        PRODUCTION_ASSISTANT = (
            62  # 制作アシスタント 制作補佐 製作補 / Production Assistant / 制作助理
        )
        PRODUCTION_COORDINATION = (
            64  # 制作コーディネーター / Production Coordination / 制作协调
        )
        WORK_ASSISTANCE = 76  # 制作協力 / 作品協力 / Work Assistance / 制作协力
        SPECIAL_THANKS = 66  # 友情協力 / Special Thanks / 特别鸣谢
        ASSISTANCE = 81  # 協力 / Assistance / 协力

    class GameStaff(IntEnum):
        DEVELOPER = 1001  # 開発元 / Developer / 开发
        PUBLISHER = 1002  # 発売元 / Publisher / 发行
        GAME_DESIGNER = 1003  # ゲームクリエイター / Game Designer / 游戏设计师
        ORIGINAL_CREATOR = 1015  # 原作
        DIRECTOR = 1016  # 監督 演出 シリーズ監督 / Director/Direction / 导演
        PRODUCER = 1032  # プロデューサー / Producer / 制作人
        PLANNING = 1028  # 企画
        SUPERVISION = 1026  # 監修 / 监修
        SCRIPT = 1004  # 腳本 / 剧本
        SERIES_COMPOSITION = 1027  # シリーズ構成 / 系列构成
        ANIMATION_DIRECTION = 1031  # 作画監督 / 作画监督
        KEY_ANIMATION = 1013  # 原画
        CHARACTER_DESIGN = (
            1008  # キャラ設定 キャラクターデザイン / Character Design / 人物设定
        )
        MECHANICAL_DESIGN = 1029  # メカニック設定 / Mechanical Design / 机械设定
        ART = 1005  # 美術 / 美工
        CG_SUPERVISION = 1023  # CG 監修 / CG 监修
        SD_KEY_ANIMATION = 1024  # SD原画
        BACKGROUND = 1025  # 背景
        SOUND_DIRECTOR = 1030  # Sound Director / 音响监督
        MUSIC = 1006  # 音楽 / 音乐
        PROGRAM = 1021  # プログラム / Program / 程序
        ANIMATION_WORK = 1014  # アニメーション制作 アニメ制作 アニメーション / Animation Work / 动画制作
        ANIMATION_DIRECTOR = 1017  # アニメーション監督 / 动画监督
        ANIMATION_SCRIPT = 1020  # アニメーション脚本 / 动画剧本
        PRODUCTION_CHIEF = 1018  # 制作总指挥
        QC = 1019  # QC / QC
        LEVEL_DESIGN = 1007  # 关卡设计
        THEME_SONG_COMPOSITION = 1009  # Theme Song Composition / 主题歌作曲
        THEME_SONG_LYRICS = 1010  # Theme Song Lyrics / 主题歌作词
        THEME_SONG_PERFORMANCE = 1011  # Theme Song Performance / 主题歌演出
        INSERTED_SONG_PERFORMANCE = 1012  # Inserted Song Performance / 插入歌演出
        ASSISTANCE = 1022  # 協力 / 协力

    class BookStaff(IntEnum):
        ORIGINAL_CREATOR = 2007  # Original Creator / Original Work / 原作
        AUTHOR = 2001  # 作者
        ARTIST = 2002  # 作画
        ILLUSTRATOR = 2003  # イラスト / 插图
        SCRIPT = 2010  # シナリオ / 脚本
        PUBLISHER = 2004  # 出版社
        SERIALIZATION_MAGAZINE = 2005  # 掲載誌 / 连载杂志
        TRANSLATOR = 2006  # 译者
        GUEST = 2008  # ゲスト / Guest / 客串
        ORIGINAL_CHARACTER_DESIGN = (
            2009  # キャラクター原案 / Original Character Design / 人物原案
        )
        LABEL = 2011  # Label / 书系
        PRODUCER = 2012  # 出品方
        BRAND = 2013  # ブランド / Brand / 图书品牌

    class MusicStaff(IntEnum):
        ARTIST = 3001  # Artist / 艺术家
        PRODUCER = 3002  # Producer / 制作人
        LABEL = 3004  # レーベル / Label / 厂牌
        COMPOSER = 3003  # Composer / 作曲
        LYRIC = 3006  # Lyric / 作词
        ARRANGE = 3008  # Arrange / 编曲
        INSTRUMENT = 3014  # Instrument / 乐器
        VOCAL = 3015  # Vocal / 声乐
        RECORDING = 3007  # Recording / 录音
        MIXING = 3013  # Mixing / 混音
        MASTERING = 3012  # Mastering / 母带制作
        ILLUSTRATOR = 3009  # Illustrator / 插图
        ORIGINAL_CREATOR = 3005  # Original Creator / Original Work / 原作
        SCENARIO = 3010  # シナリオ / Scenario / 脚本
        PUBLISHER = 3011  # 音楽出版社 / O.P. / 出版方

    class RealStaff(IntEnum):
        ORIGINAL_CREATOR = 4001  # creator / 原作
        DIRECTOR = 4002  # director / 导演
        CREATIVE_DIRECTOR = 4013  # creative director / 创意总监
        WRITER = 4003  # writer / 编剧
        COMPOSER = 4004  # composer / 音乐
        EXECUTIVE_PRODUCER = 4005  # 製作総指揮 / executive producer / 执行制片人
        CO_EXEC = 4006  # co exec / 共同执行制作
        PRODUCER = 4007  # プロデューサー / producer / 制片人/制作人
        SUPERVISING_PRODUCER = 4008  # supervising producer / 监制
        CONSULTING_PRODUCER = 4009  # consulting producer / 副制作人/制作顾问
        STORY = 4010  # story / 故事
        STORY_EDITOR = 4011  # story editor / 编审
        EDITOR = 4012  # editor / 剪辑
        CINEMATOGRAPHY = 4014  # cinematography / 摄影
        THEME_SONG_PERFORMANCE = 4015  # Theme Song Performance / 主题歌演出
        ACTOR = 4016  # Actor / 主演
        SUPPORTING_ACTOR = 4017  # Supporting Actor / 配角
        PRODUCTION = 4018  # 製作 製作スタジオ / Production / 制作
        PRESENT = 4019  # 配給 / Present / 出品


class Tag(BaseModel):
    """Tag model for subjects."""

    name: str
    count: int


class ScoreDetails(BaseModel):
    """Score distribution details."""

    score_1: int = Field(0, alias="1")
    score_2: int = Field(0, alias="2")
    score_3: int = Field(0, alias="3")
    score_4: int = Field(0, alias="4")
    score_5: int = Field(0, alias="5")
    score_6: int = Field(0, alias="6")
    score_7: int = Field(0, alias="7")
    score_8: int = Field(0, alias="8")
    score_9: int = Field(0, alias="9")
    score_10: int = Field(0, alias="10")


class Favorite(BaseModel):
    """Favorite statistics."""

    wish: int
    done: int
    doing: int
    on_hold: int
    dropped: int


class Subject(BaseModel):
    """Subject model (anime, book, game, etc.)."""

    model_config = _config

    id: int
    type: SubjectType
    name: str
    name_cn: str
    infobox: str
    platform: int
    summary: str
    nsfw: bool
    tags: list[Tag]
    score: float
    score_details: Optional[ScoreDetails] = None
    rank: int
    date: str | None

    favorite: Favorite
    series: bool
    meta_tags: Optional[list[str]] = None

    @field_validator('date')
    def strip_date(cls, v: Optional[str]) -> Optional[str]:
        return launder_date(v)


class Person(BaseModel):
    """Person model (individual, company, association)."""

    model_config = _config

    id: int
    name: str
    type: PersonType
    career: List[str] = Field(default_factory=list)
    infobox: str
    summary: str
    comments: int
    collects: int


class Character(BaseModel):
    """Character model."""

    model_config = _config

    id: int
    role: CharacterRole
    name: str
    infobox: str
    summary: str
    comments: int
    collects: int


class Episode(BaseModel):
    """Episode model."""

    model_config = _config

    id: int
    name: str
    name_cn: str
    description: str
    airdate: str | None = None
    disc: int
    duration: str
    subject_id: int
    sort: int | float
    type: EpisodeType

    @field_validator('airdate')
    def strip_date(cls, v: Optional[str]) -> Optional[str]:
        return launder_date(v)


class SubjectRelation(BaseModel):
    """Relation between subjects."""

    model_config = _config

    subject_id: int
    relation_type: SubjectRelationType
    related_subject_id: int
    order: int


class SubjectCharacter(BaseModel):
    """Relation between subject and character."""

    model_config = _config

    character_id: int
    subject_id: int
    type: CharacterSubjectType
    order: int


class SubjectPerson(BaseModel):
    """Relation between subject and person."""

    model_config = _config

    person_id: int
    subject_id: int
    position: (
        SubjectPersonType.AnimeStuff
        | SubjectPersonType.GameStaff
        | SubjectPersonType.BookStaff
        | SubjectPersonType.MusicStaff
        | SubjectPersonType.RealStaff
    )


class PersonCharacter(BaseModel):
    """Relation between person and character."""

    model_config = _config

    person_id: int
    subject_id: int
    character_id: int
    summary: str
