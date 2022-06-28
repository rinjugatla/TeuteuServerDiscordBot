import os, aiohttp, json
from models.bot.apex_user_rank_model import ApexUserRankModel
if os.path.exists('pro.mode'):
    import secret.secret_pro as secret
    import secret.const_pro as const
else:
    import secret.secret_dev as secret
    import secret.const_dev as const

class ApexLegendsStatusAPI():
    @staticmethod
    async def get_user_by_uid(uid: int, platform: str) -> ApexUserRankModel:
        """APIからユーザのランク情報を取得
        """
        base_url = 'https://api.mozambiquehe.re/bridge?uid=:uid:&platform=:platform:&merge=true&removeMerged=true'
        url = base_url.replace(':uid:', str(uid)).replace(':platform:', platform)
        user = await ApexLegendsStatusAPI.__get_user(url)
        return user

    @staticmethod
    async def get_user_by_name(name: str, platform: str) -> ApexUserRankModel:
        """APIからユーザのランク情報を取得
        """
        base_url = 'https://api.mozambiquehe.re/bridge?player=:name:&platform=:platform:&merge=true&removeMerged=true'
        url = base_url.replace(':name:', name).replace(':platform:', platform)
        user = await ApexLegendsStatusAPI.__get_user(url)
        return user

    @staticmethod
    async def __get_user(url: str) -> ApexUserRankModel:
        """ApexLegendsUserStatus
            https://apexlegendsapi.com/#query-by-name
            https://apexlegendsapi.com/#query-by-uid

        Args:
            url (str): エンドポイント

        Returns:
            ApexUserRankModel: ランク情報を含むユーザ情報
        """
        async with aiohttp.ClientSession() as session:
            headers = {
                'Content-Type': 'application/json;',
                'Authorization': secret.APEX_TOKEN
            }
            async with session.post(url=url, headers=headers) as response:
                if response.status != 200:
                    return None

                # header: Content-Type: text/plain;charset=UTF-8なのでresponse.json()は利用不可
                data = json.loads(await response.text())
                user = ApexUserRankModel(data)
                return user