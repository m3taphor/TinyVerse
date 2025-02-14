import ua_generator
from ua_generator.options import Options
from ua_generator.data.version import VersionRange


def generate_random_user_agent(platform='android', browser='chrome', min_version=110, max_version=129):
    options = Options(version_ranges={'chrome': VersionRange(min_version, max_version)})
    return ua_generator.generate(browser=browser, platform=platform, options=options).text
