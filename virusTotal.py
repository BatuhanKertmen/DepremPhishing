import vt


def virusTotal(url, api_key):
    try:
        client = vt.Client(api_key)

        url_id = vt.url_id(url)
        response = client.get_object("/urls/{}", url_id)

        return response.last_analysis_stats['malicious']
    except:
        return -1


