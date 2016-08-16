
def captcha_solver(name, s, data, recaptcha=True):
    try:
        log.debug("{name}: captcha solver is waiting captcha".format(name=name))
        if recaptcha:
            captcha_js_url = re.search(r"(http://www\.google\.com/recaptcha/api/challenge\?k=.*?)\">", data).group(1)
            r = s.get(captcha_js_url)
            challenge = re.search("challenge : '([^']*)'", r.text).group(1)
            r = s.get("http://www.google.com/recaptcha/api/image?c=" + challenge)
            tmp_file = NamedTemporaryFile(mode="w+b", suffix=".jpg")
            tmp_file.write(r.content)
            tmp_file.flush()
            result = (AntiGate(antigate_key, tmp_file.name), challenge)
            tmp_file.close()
            return result
        else:
            r = s.get(data)
            tmp_file = NamedTemporaryFile(mode="w+b", suffix=".gif")
            tmp_file.write(r.content)
            tmp_file.flush()
            result = AntiGate(antigate_key, tmp_file.name)
            tmp_file.close()
            return result

    except Exception as error:
        log.exception("{name}: captcha solver error:  {error}".format(error=error, name=name))
        return (False, False)
