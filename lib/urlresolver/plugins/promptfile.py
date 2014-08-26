'''
urlresolver XBMC Addon
Copyright (C) 2013 Bstrdsmkr

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import re, urllib2, os, xbmcgui
from urlresolver import common

#SET ERROR_LOGO# THANKS TO VOINAGE, BSTRDMKR, ELDORADO
error_logo = os.path.join(common.addon_path, 'resources', 'images', 'redx.png')

class PromptfileResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "promptfile"
    domains = [ "promptfile.com" ]

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        try:
            html = self.net.http_GET(web_url).content
            data = {}
            r = re.findall(r'type="hidden"\s*name="(.+?)"\s*value="(.*?)"', html)
            for name, value in r:
                data[name] = value
            html = self.net.http_POST(web_url, data).content
            # Find a name for the video
            t = re.search('<span.*title="(.+?)">', html)
            if t:
                self._labes['name']=t.group(1)
            html = re.compile(r'clip\s*:\s*\{.*?url\s*:\s*[\"\'](.+?)[\"\']', re.DOTALL).search(html)
            if not html:
                raise Exception ('File Not Found or removed')
            stream_url = html.group(1)
            return stream_url

        except urllib2.URLError, e:
            common.addon.log_error(self.name + ': got http error %d fetching %s' %
                                   (e.code, web_url))
            common.addon.show_small_popup('Error','Http error: '+str(e), 5000, error_logo)
            return self.unresolvable(code=3, msg=e)

        except Exception, e:
            common.addon.log_error('**** Promptfile Error occured: %s' % e)
            common.addon.show_small_popup(title='[B][COLOR white]PROMPTFILE[/COLOR][/B]', msg='[COLOR red]%s[/COLOR]' % e, delay=5000, image=error_logo)
            return self.unresolvable(code=0, msg=e)

    def get_url(self, host, media_id):
        return 'http://www.promptfile.com/%s' % (media_id)

    def get_host_and_id(self, url):
        r = re.search('//(.+?)/(.+)', url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return (re.match('http://(www.)?promptfile.com/l/' +
                         '[0-9A-Za-z\-]+', url) or
                         'promptfile' in host)
