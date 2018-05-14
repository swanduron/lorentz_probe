import tools
import config
import optparse
import json

parser = optparse.OptionParser()
parser.add_option('-r', '--renew', dest='renew', action="store_true", help='Use this option to re-generate a server_info.ini file.')
parser.add_option('-f', '--refresh', dest='refresh', action="store_true", help='Reload ini file into program')
parser.add_option('-w', '--work', dest='working', action="store_true", help='Run probe at once.')
options, args = parser.parse_args()

if options.renew:
    tools.get_config_file(renew_flag=True, load_flag=False)
elif options.refresh:
    tools.get_config_file(renew_flag=False, load_flag=True)
elif options.working:
    with open(config.JSON_FILE_PATH) as json_file_obj:
        working_json = json.load(json_file_obj)
    tools.ping_probe(working_json)
    tools.check_ping_status(working_json)
else:
    print('Nothing todo')