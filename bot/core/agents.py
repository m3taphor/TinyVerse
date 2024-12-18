import ua_generator

def generate_ua(device='desktop', platform='windows', browser='edge'):
    random_ua = ua_generator.generate(device=device, platform=platform, browser=browser)
    return str(random_ua)