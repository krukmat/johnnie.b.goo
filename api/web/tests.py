# Create your tests here.
from django.test.testcases import SimpleTestCase
from mock import patch, MagicMock
from tasks import scrape_track, generate_report
from utils import DiscogsDriver, FileHandler


class TestTasks(SimpleTestCase):
    """ TODO: Mock delete file method in tests
    """

    @patch('youtube_dl.YoutubeDL.extract_info', MagicMock(return_value={u'formats':
                                                                            [{u'abr': 256,
                                                                                  u'acodec': u'aac',
                                                                                  u'asr': 44100,
                                                                        u'container': u'm4a_dash',
                                                                        u'ext': u'm4a',
                                                                        u'filesize': 12226728,
                                                                        u'format': u'141 - audio only (DASH audio)',
                                                                        u'format_id': '141',
                                                                        u'format_note': u'DASH audio',
                                                                        u'fps': None,
                                                                        u'height': None,
                                                                        u'http_headers': {
                                                                            u'Accept': u'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                                                            u'Accept-Charset': u'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                                                                            u'Accept-Encoding': u'gzip, deflate',
                                                                            u'Accept-Language': u'en-us,en;q=0.5',
                                                                            u'User-Agent': u'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20150101 Firefox/20.0 (Chrome)'},
                                                                        u'preference': -50,
                                                                        u'tbr': 256,
                                                                        u'url': 'https://r6---sn-j5cax8pnpvo-x1xr.googlevideo.com/videoplayback?id=0a4a26de07f9ed8c&itag=141&source=youtube&requiressl=yes&pcm2cms=yes&pl=21&mm=31&ms=au&mv=m&ratebypass=yes&mime=audio/mp4&gir=yes&clen=12226728&lmt=1432526753377394&dur=383.477&signature=2D470B49E062C94E4CDD3F53C8A6590BB1CBC4B5.4EFAD3DE7E879E4B4F77F05E13064A3694160099&sver=3&upn=qC3qkhUDvWg&key=dg_yt0&fexp=916633,938690,9406368,9406813,9407662,9408142,9408254,9408420,9408710,9408967,9409249,9413503,9415304,952612&mt=1433084293&ip=181.167.225.228&ipbits=0&expire=1433105967&sparams=ip,ipbits,expire,id,itag,source,requiressl,pcm2cms,pl,mm,ms,mv,ratebypass,mime,gir,clen,lmt,dur',
                                                                        u'vcodec': u'none',
                                                                        u'width': None}],
                                                                        u'display_id': 'Ckom3gf57Yw'
                                                                        }
    ))
    @patch('requests.get', MagicMock())
    def test_scrape_track(self):
        # Normal case
        with patch('web.utils.YouTubeExtractor.search_youtube_links',
                   MagicMock(return_value=u'https://www.youtube.com/watch?v=Ckom3gf57Yw')):
            task = scrape_track.delay('Lalalala', 'tmp')
            name, folder = task.get()
            self.assertEqual(name, 'Lalalala')
            self.assertEqual(folder, u'/tmp/Ckom3gf57Yw.mp3')
            FileHandler.delete_file('/tmp/Ckom3gf57Yw.mp3')

    @patch('requests.get', MagicMock())
    def test_scrape_track_youtube_exception(self):
        # Case when an exception raised in search_youtube_links
        with patch('web.utils.YouTubeExtractor.search_youtube_links',
                    MagicMock(side_effect=Exception('Exception'))):
            task = scrape_track.delay('Lalalala', 'tmp')
            name, folder = task.get()
            self.assertEqual(name, False)
            self.assertEqual(folder, False)

    @patch('youtube_dl.YoutubeDL.extract_info', MagicMock(return_value={u'formats':
                                                                                    [{u'abr': 256,
                                                                                      u'acodec': u'aac',
                                                                                      u'asr': 44100,
                                                                                      u'container': u'm4a_dash',
                                                                                      u'ext': u'm4a',
                                                                                      u'filesize': 12226728,
                                                                                      u'format': u'141 - audio only (DASH audio)',
                                                                                      u'format_id': '141',
                                                                                      u'format_note': u'DASH audio',
                                                                                      u'fps': None,
                                                                                      u'height': None,
                                                                                      u'http_headers': {
                                                                                          u'Accept': u'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                                                                          u'Accept-Charset': u'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                                                                                          u'Accept-Encoding': u'gzip, deflate',
                                                                                          u'Accept-Language': u'en-us,en;q=0.5',
                                                                                          u'User-Agent': u'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20150101 Firefox/20.0 (Chrome)'},
                                                                                      u'preference': -50,
                                                                                      u'tbr': 256,
                                                                                      u'url': 'https://r6---sn-j5cax8pnpvo-x1xr.googlevideo.com/videoplayback?id=0a4a26de07f9ed8c&itag=141&source=youtube&requiressl=yes&pcm2cms=yes&pl=21&mm=31&ms=au&mv=m&ratebypass=yes&mime=audio/mp4&gir=yes&clen=12226728&lmt=1432526753377394&dur=383.477&signature=2D470B49E062C94E4CDD3F53C8A6590BB1CBC4B5.4EFAD3DE7E879E4B4F77F05E13064A3694160099&sver=3&upn=qC3qkhUDvWg&key=dg_yt0&fexp=916633,938690,9406368,9406813,9407662,9408142,9408254,9408420,9408710,9408967,9409249,9413503,9415304,952612&mt=1433084293&ip=181.167.225.228&ipbits=0&expire=1433105967&sparams=ip,ipbits,expire,id,itag,source,requiressl,pcm2cms,pl,mm,ms,mv,ratebypass,mime,gir,clen,lmt,dur',
                                                                                      u'vcodec': u'none',
                                                                                      u'width': None}],
                                                                                u'display_id': 'Ckom3gf57Yw'
            }
            ))
    @patch('requests.get', MagicMock(side_effect=Exception()))
    def test_scrape_track_request_exception(self):
        with patch('web.utils.YouTubeExtractor.search_youtube_links',
                   MagicMock(return_value=u'https://www.youtube.com/watch?v=Ckom3gf57Yw')):
            task = scrape_track.delay('Lalalala', 'tmp')
            name, folder = task.get()
            self.assertEqual(name, False)
            self.assertEqual(folder, False)

    @patch('youtube_dl.YoutubeDL.extract_info', MagicMock(return_value={u'formats':
                                                                                        [{u'abr': 256,
                                                                                          u'acodec': u'aac',
                                                                                          u'asr': 44100,
                                                                                          u'container': u'm4a_dash',
                                                                                          u'ext': u'm4a',
                                                                                          u'filesize': 12226728,
                                                                                          u'format': u'141 - audio only (DASH audio)',
                                                                                          u'format_id': '141',
                                                                                          u'format_note': u'DASH audio',
                                                                                          u'fps': None,
                                                                                          u'height': None,
                                                                                          u'http_headers': {
                                                                                              u'Accept': u'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                                                                              u'Accept-Charset': u'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                                                                                              u'Accept-Encoding': u'gzip, deflate',
                                                                                              u'Accept-Language': u'en-us,en;q=0.5',
                                                                                              u'User-Agent': u'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20150101 Firefox/20.0 (Chrome)'},
                                                                                          u'preference': -50,
                                                                                          u'tbr': 256,
                                                                                          u'url': 'https://r6---sn-j5cax8pnpvo-x1xr.googlevideo.com/videoplayback?id=0a4a26de07f9ed8c&itag=141&source=youtube&requiressl=yes&pcm2cms=yes&pl=21&mm=31&ms=au&mv=m&ratebypass=yes&mime=audio/mp4&gir=yes&clen=12226728&lmt=1432526753377394&dur=383.477&signature=2D470B49E062C94E4CDD3F53C8A6590BB1CBC4B5.4EFAD3DE7E879E4B4F77F05E13064A3694160099&sver=3&upn=qC3qkhUDvWg&key=dg_yt0&fexp=916633,938690,9406368,9406813,9407662,9408142,9408254,9408420,9408710,9408967,9409249,9413503,9415304,952612&mt=1433084293&ip=181.167.225.228&ipbits=0&expire=1433105967&sparams=ip,ipbits,expire,id,itag,source,requiressl,pcm2cms,pl,mm,ms,mv,ratebypass,mime,gir,clen,lmt,dur',
                                                                                          u'vcodec': u'none',
                                                                                          u'width': None}],
                                                                                    u'display_id': 'Ckom3gf57Yw'
                }
    ))
    @patch('requests.get', MagicMock())
    @patch('__builtin__.open', MagicMock(side_effect=Exception()))
    @patch('web.tasks.StorageException')
    def test_scrape_error_saving_file_exception(self, storage):
        with patch('web.utils.YouTubeExtractor.search_youtube_links',
                   MagicMock(return_value=u'https://www.youtube.com/watch?v=Ckom3gf57Yw')):
            task = scrape_track.delay('Lalalala', 'tmp')
            name, folder = task.get()
            self.assertRaises(storage)
            self.assertEqual(name, False)
            self.assertEqual(folder, False)

    @patch('web.utils.FingerPrintDriver.generate_fingerprint_from_list', MagicMock())
    @patch('__builtin__.open', MagicMock())
    def test_generate_report(self):
        # False positive cases
        results = [(False, False), ('dude', 'dude'), (False, False)]
        with patch('web.utils.FileHandler.delete_file') as deletefile:
            task = generate_report.delay(results)
            task.get()
            deletefile.assert_any_call('dude')
            self.assertEqual(deletefile.call_count, 2)

        # All positive cases
        results = [('dude3', 'dude2'), ('dude', 'dude'), ('dude4', 'dude4')]
        with patch('web.utils.FileHandler.delete_file') as deletefile:
            task = generate_report.delay(results)
            task.get()
            deletefile.assert_any_call('dude')
            deletefile.assert_any_call('dude2')
            deletefile.assert_any_call('dude4')
            self.assertEqual(deletefile.call_count, 4)

    def test_generate_tasks(self):
        self.skipTest("Check PATH Issue")

    def test_discogs_scrape_artists(self):
        self.skipTest("Check PATH Issue")

    def test_discogs_scrape_artist(self):
        self.skipTest("Check PATH Issue")


class TestFingerPrintDriver(SimpleTestCase):
    pass


class TestDiscogsDriver(SimpleTestCase):
    def test_get_discogs_artist_track(self):
        artists = ['lalalalalsdsdsddsa', 'Nirvana']
        valid_artists = DiscogsDriver.get_valid_artists(artists)
        self.assertEqual(len(valid_artists), 1)
        with patch('urllib2.Request') as request:
            request.side_effect = Exception()
            valid_artists = DiscogsDriver.get_valid_artists(artists)
            self.assertEqual(len(valid_artists), 0)

    def test_get_discogs_artist_track(self):
        result = DiscogsDriver().get_discogs_artist_track('88495')
        self.assertEqual(result, {
            'tracks': [u'Hoot Nanny Hoot ', u'Do You Remember', u'Shame And Scandal', u'The Jerk', u'Dancing Shoes',
                       u'Shame & Scandal', u'Dancing Time', u'Treat Me Good', u'I Am The Toughest', u'No Faith',
                       u'Trying To Keep A Good Man Down ', u'Oh My Darling', u'Bend Down Low', u'Mellow Mood',
                       u'Its Only Time', u'Tall In The Saddle', u'Stepping Razor', u'Vampire', u'Cat Woman',
                       u'Selassie Serenade'], 'videos': [
            {u'duration': 190, u'embed': True, u'uri': u'http://www.youtube.com/watch?v=Ag5MQeS0J8U',
             u'description': u'peter touch and the wailers - hoot nanny hoot (island)',
             u'title': u'peter touch and the wailers - hoot nanny hoot (island)'},
            {u'duration': 183, u'embed': True, u'uri': u'http://www.youtube.com/watch?v=CTsYEM02I20',
             u'description': u'The Wailers -  Shame and Scandal', u'title': u'The Wailers -  Shame and Scandal'},
            {u'duration': 167, u'embed': True, u'uri': u'http://www.youtube.com/watch?v=OlSI8uj8rnQ',
             u'description': u'The Wailers -  Dancing Shoes - coxsone records - 1966 ska',
             u'title': u'The Wailers -  Dancing Shoes - coxsone records - 1966 ska'},
            {u'duration': 183, u'embed': True, u'uri': u'http://www.youtube.com/watch?v=CTsYEM02I20',
             u'description': u'The Wailers -  Shame and Scandal', u'title': u'The Wailers -  Shame and Scandal'},
            {u'duration': 155, u'embed': True, u'uri': u'http://www.youtube.com/watch?v=Pov_z6KFM40',
             u'description': u"Peter & Rita   It's Only Time", u'title': u"Peter & Rita   It's Only Time"},
            {u'duration': 176, u'embed': True, u'uri': u'http://www.youtube.com/watch?v=IJ-Aj2Bkm2Q',
             u'description': u'Rolando Al & his, Soul Bros Tall In The Saddle',
             u'title': u'Rolando Al & his, Soul Bros Tall In The Saddle'},
            {u'duration': 351, u'embed': True, u'uri': u'http://www.youtube.com/watch?v=9o_jVHmU_V4',
             u'description': u'Peter Tosh - Stepping Razor  (HD)', u'title': u'Peter Tosh - Stepping Razor  (HD)'},
            {u'duration': 451, u'embed': True, u'uri': u'http://www.youtube.com/watch?v=Ym6910e4o3Y',
             u'description': u'Peter Tosh - Selassie Serenade b/w Glen Adams - Cat Woman',
             u'title': u'Peter Tosh - Selassie Serenade b/w Glen Adams - Cat Woman'}]}
        )


