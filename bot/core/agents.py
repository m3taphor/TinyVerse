import ua_generator

def generate_ua(device='mobile', platform='android', browser='chrome'):
    random_ua = ua_generator.generate(device=device, platform=platform, browser=browser)
    return str(random_ua)