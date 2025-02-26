import re

def convert_text(text):
    text = text.lower()

    text = re.sub(r'à|á|ạ|ả|ã|â|ầ|ấ|ậ|ẩ|ẫ|ă|ằ|ắ|ặ|ẳ|ẵ', 'a', text)
    text = re.sub(r'è|é|ẹ|ẻ|ẽ|ê|ề|ế|ệ|ể|ễ', 'e', text)
    text = re.sub(r'ì|í|ị|ỉ|ĩ', 'i', text)
    text = re.sub(r'ò|ó|ọ|ỏ|õ|ô|ồ|ố|ộ|ổ|ỗ|ơ|ờ|ớ|ợ|ở|ỡ', 'o', text)
    text = re.sub(r'ù|ú|ụ|ủ|ũ|ư|ừ|ứ|ự|ử|ữ', 'u', text)
    text = re.sub(r'ỳ|ý|ỵ|ỷ|ỹ', 'y', text)
    text = re.sub(r'đ', 'd', text)
    
    text = re.sub(r'\u0300|\u0301|\u0303|\u0309|\u0323', '', text)
    text = re.sub(r'\u02C6|\u0306|\u031B', '', text)

    text = re.sub(r'\(.*?\)|&|,|-| |__+', '_', text).strip('_')
    while('__' in text):
        text = re.sub(r'__', '_', text)
    text = text.strip('_')
    return text