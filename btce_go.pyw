#-*- coding: UTF-8 -*-

from PyQt4 import QtGui, QtCore
import sys, urllib2, socket, ssl, httplib, json, time
from datetime import datetime
from decimal import *
from ConfigParser import SafeConfigParser

__version__ = 'BTC-E Go! 1.2.9'

class Settings:
    def __init__(self):
        self.filename = 'settings.ini'
        self.cfgParser = SafeConfigParser()
        self.cfgParser.read(self.filename)
        
    def get(self, key):
        return self.cfgParser.get('settings', key)
    
    def set(self, key, value):
        self.cfgParser.set('settings', key, str(value) )
        self.save()
    
    def save(self):
        with open(self.filename, 'wb') as config:
            self.cfgParser.write(config)

class CryptoCource(QtCore.QThread):
    def __init__(self, coin_ids, request_timeout):
        QtCore.QThread.__init__(self)
        self.coin_ids         = '-'.join(coin_ids)
        self.request_timeout  = float(request_timeout)
        self.time_start       = time.time()
        self.errors           = ''
        self.finished.connect(self.threadFinished)
        
    def run(self):
        try:  
            response = urllib2.urlopen('https://btc-e.com/api/3/ticker/%s?ignore_invalid=1' % self.coin_ids, None, self.request_timeout)          
            decoded_json_string = str(response.read())
            
            try:
                self.emit(QtCore.SIGNAL("complete_get_crypto_cource"), json.loads(decoded_json_string))
            except ValueError:
                self.errors += '%s -> %s' % (time.strftime("%H:%M:%S"), 'JSON parse error<br/>')
                
        except socket.error as e:
            self.errors += '%s -> %s' % (time.strftime("%H:%M:%S"), 'Socket error = %s<br/>' % e)      
        except urllib2.HTTPError, e:
            self.errors += '%s -> %s' % (time.strftime("%H:%M:%S"), 'HTTPError = %s <br/>' % str(e.code))
        except urllib2.URLError, e:
            self.errors += '%s -> %s' % (time.strftime("%H:%M:%S"), 'URLError = %s <br/>' % str(e.reason))
        except httplib.HTTPException, e:
            self.errors += '%s -> %s' % (time.strftime("%H:%M:%S"), 'HTTPException = %s <br/>'  % str(e.reason))
        except socket.timeout:
            self.errors += '%s -> %s' % (time.strftime("%H:%M:%S"), 'Timeout connection <br/>')
        except ssl.SSLError, e:
            self.errors += '%s -> %s' % (time.strftime("%H:%M:%S"), 'ssl.SSLError = %r<br/>' % str(e))
            
        if self.errors:
            self.emit(QtCore.SIGNAL("system_logger"), self.errors)
                
    def threadFinished(self):
        self.emit(QtCore.SIGNAL("run_update_timer"), (time.time() - self.time_start) )

class About(QtGui.QDialog):
    def __init__(self, parent=None):
        super(About, self).__init__(parent)
        
        self.setFixedSize(550, 400)
        self.setWindowTitle(__version__)
        
        self.pageContent()

    def pageContent(self):
        content = QtGui.QLabel(self)
        content.setText(u'''<div align="center" style="font-size: 12px;">
                                <h4> {version} </h4>
                                Программа для мониторинга состояния цен биржи BTC-E.com<br/>
                                Разработано для всех, кто знает что такое криптовалюта =)<br/><br/>
                                <b>Программа и исходный код распространяются бесплатно.</b> <br/>
                            </div>
                            
                            Любой желающий может поучаствовать в разработке программы:<br/>
                            1) Принимаем ваши пожелания и предложения <a href="http://vk.com/btce_go">Официальная группа ВК</a> <br/>
                            2) Скачать последнюю версию и узнать новости проекта можно на <a href="http://sanzstez.github.io/btc-e.go/">странице проекта в Github</a> <br/>
                            3) ... А в этом пункте разработчик как всегда просит подкинуть ему денег на пиво. 
                                   Ну что же, пожалуй не будем нарушать традицию... :) <br/>
                            
                            <table width="100%"> 
                              <tr>
                                  <td align="center" style="color: #00732F;"><b>Bitcoin (BTC)</b></td>
                                  <td align="center" style="color: #00732F;"><b>Litecoin (LTC)</b></td>
                              </tr>
                              <tr>
                                  <td align="center" style="font-size: 10px;">
                                      <b>151xG1K5pUVGbvguYd2vPfBSTy66Uifoq4</b>
                                  </td>
                                  <td align="center" style="font-size: 10px;">
                                      <b>LVdozFjRfpWJb7j5kDRrkmvMjBaFsm1Wza</b>
                                  </td>
                              </tr>
                              <tr>
                                  <td align="center">
                                      <img width="150" height="150" src="resources/151xG1K5pUVGbvguYd2vPfBSTy66Uifoq4.png"/>
                                  </td>
                                  <td align="center">
                                      <img width="150" height="150" src="resources/LVdozFjRfpWJb7j5kDRrkmvMjBaFsm1Wza.png"/>
                                  </td>
                              </tr>
                           </table>  
                        '''.format(version = __version__))
        
        content.setAlignment(QtCore.Qt.AlignTop)
        content.setGeometry(QtCore.QRect(0, 10, 550, 400))
        content.setWordWrap(True)
        content.setOpenExternalLinks(True)
        content.setMargin(5)
        content.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse | QtCore.Qt.TextSelectableByKeyboard | QtCore.Qt.LinksAccessibleByMouse)
        
#class AlarmSettings(QtGui.QDialog):
#    def __init__(self, parent=None):
#        super(About, self).__init__(parent)
#        
#        self.setFixedSize(550, 400)
#        self.setWindowTitle(__version__)
#        
#        self.pageContent()
#
#    def pageContent(self):
#        pass
        
class Program(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.initProgramSettings()
        
        self.setWindowTitle(__version__)
        self.setWindowIcon(self.program_icon)
        self.setWindowFlags(self.window_fix)
        
        self.initializeSystemTray()
        self.initProgramSettings()
        self.initHistoryStack()
        self.initCryptoCourcesView()
        self.runCryptoCourcesThread()
        
        self.setFixedSize(450, self.widget_height + self.logger_offset + 20)
        
        self.aboutPage = About(self)
        
        self.aboutPageButton = QtGui.QToolButton(self)
        self.aboutPageButton.setIcon(QtGui.QIcon('resources/info.png'))
        self.aboutPageButton.move(427, self.widget_height)
        self.aboutPageButton.setIconSize(QtCore.QSize(18, 18))
        self.aboutPageButton.setStyleSheet('''
                                            QToolButton {  border: 0; background: transparent; } 
                                            QToolTip    { color: #000; }
                                           ''')
        self.aboutPageButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.aboutPageButton.setToolTip(u'О программе')
        self.connect(self.aboutPageButton, QtCore.SIGNAL('clicked()'), self.aboutPage, QtCore.SLOT('show()'))
         
        self.takeScreenButton = QtGui.QToolButton(self)
        self.takeScreenButton.setIcon(QtGui.QIcon('resources/screenshot.png'))
        self.takeScreenButton.move(387, self.widget_height)
        self.takeScreenButton.setIconSize(QtCore.QSize(18, 18))
        self.takeScreenButton.setStyleSheet('''
                                              QToolButton {  border: 0; background: transparent; } 
                                              QToolTip    { color: #000; }
                                            ''')
        self.takeScreenButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.takeScreenButton.setToolTip(u'Сделать скриншот курсов (Ctrl+Q)')
        self.takeScreenButton.setShortcut('Ctrl+Q')
        self.connect(self.takeScreenButton, QtCore.SIGNAL('clicked()'), self.takeScreenshot)
        
        self.toggleWindowStateButton = QtGui.QToolButton(self)
        self.toggleWindowStateButton.setIcon(QtGui.QIcon('resources/fixed.png'))
        self.toggleWindowStateButton.move(367, self.widget_height)
        self.toggleWindowStateButton.setIconSize(QtCore.QSize(18, 18))
        self.toggleWindowStateButton.setStyleSheet('''
                                                    QToolButton {  border: 0; background: transparent; } 
                                                    QToolTip    { color: #000; }
                                                   ''')
        self.toggleWindowStateButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.toggleWindowStateButton.setToolTip(u'Поверх всех окон')
        self.connect(self.toggleWindowStateButton, QtCore.SIGNAL('clicked()'), self.toggleWindowState)
        
        self.toggleLoggerButton = QtGui.QToolButton(self)
        self.toggleLoggerButton.setIcon(QtGui.QIcon('resources/console.png'))
        self.toggleLoggerButton.move(407, self.widget_height)
        self.toggleLoggerButton.setIconSize(QtCore.QSize(18, 18))
        self.toggleLoggerButton.setStyleSheet('''
                                               QToolButton {  border: 0; background: transparent; } 
                                               QToolTip    { color: #000; }
                                              ''')
        self.toggleLoggerButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.toggleLoggerButton.setToolTip(u'Переключить консоль')
        self.connect(self.toggleLoggerButton, QtCore.SIGNAL('clicked()'), self.toggleLoggerAction)
        
        self.systemLogger = QtGui.QTextEdit(self)
        self.systemLogger.setGeometry(QtCore.QRect(0, self.widget_height + 20, 450, 80))
        self.systemLogger.setText(u'Логгер ошибок активен')
        self.systemLogger.setStyleSheet('QTextEdit { background: black; color: green; font-size: 9px; } ')
        if self.settings.get('show_logger') == "1": self.systemLogger.setVisible(True)
        
        self.updateTime = QtGui.QLabel(self)
        self.updateTime.setGeometry(QtCore.QRect(3, self.widget_height, 360, 20))
        self.updateTime.setStyleSheet('background: transparent; font-weight: bold; font-size: 11px;')
        
        self.originalPixmap = None
        self.originalPixmap = QtGui.QPixmap.grabWidget(self, QtCore.QRect(0, 0, 450, self.widget_height + 3))  
        
    def initHistoryStack(self):
        self.history = {}
        
        for coin in self.__crypto_currency__:
            self.history[coin] = {'buy' : None, 'sell' : None, 'diff_buy' : None, 'diff_sell' : None}
  
    def initCryptoCourcesView(self):
        
        #self.alarm_buttons = self.alarm_labels = {}
        
        for index, item in enumerate(self.__crypto_currency__):
            coin_master, coin_slave = item.split('_')
            
            label_currency = setattr(self, item, QtGui.QLabel(self)) 
            label_currency = getattr(self, item) 
            
            text = u'''      
                    <table width="100%" height="90" style="color: #186F8F; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f0f0ff, stop: 0.4 #f4f4ff, stop: 0.5 #e7e7ff, stop: 1.0 #d0d9f0);"> 
                      <tr>
                        <td align="center" style="font-size: 12px; padding: 5px 0px 0px 0px;"><b>Обновление данных курса {master} -> {slave} ...</b></td>
                      <tr>
                        <td align="center"> <img src="resources/wait.png"/></td>
                      </tr>
                   </table>
                   '''.format(master=self.coindata[coin_master]['iso'], slave=self.coindata[coin_slave]['iso'])
            
            label_currency.setText(text)
            label_currency.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
            label_currency.setGeometry(QtCore.QRect(0, index*95 + 4, 450, 90))
            label_currency.setStyleSheet('background: #F2F2F2;')
    
            label_icon_currency_master = QtGui.QLabel(self)
            label_icon_currency_master.setGeometry(4, index*95 + 5, 40, 40)
            label_icon_currency_master.setToolTip(self.cryptoCoinInfo(coin_master, coin_slave))
            label_icon_currency_master.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
            label_icon_currency_master.setStyleSheet('''
                                                      QLabel   {  border: 0; background: transparent; } 
                                                      QToolTip { color: #000; }
                                                      ''')
            label_icon_currency_master.setPixmap(QtGui.QPixmap('resources/%s.png' % coin_master))
            label_icon_currency_master.setScaledContents(True)
            
            label_icon_currency_slave = QtGui.QLabel(self)
            label_icon_currency_slave.setGeometry(28, index*95 + 25, 20, 20)
            label_icon_currency_slave.setToolTip(self.cryptoCoinInfo(coin_master, coin_slave))
            label_icon_currency_slave.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
            label_icon_currency_slave.setStyleSheet('''
                                                      QLabel   {  border: 0; background: transparent; } 
                                                      QToolTip { color: #000; }
                                                    ''')
            label_icon_currency_slave.setPixmap(QtGui.QPixmap('resources/%s.png' % coin_slave))     
            label_icon_currency_slave.setScaledContents(True)  
            
            #self.alarm_labels[item] = QtGui.QLabel(self)
            #self.alarm_labels[item].setGeometry(0, 90 + index*90, 450, 20)
            #self.alarm_buttons[item] = QtGui.QToolButton(self)
            #self.alarm_buttons[item].setIcon(QtGui.QIcon('resources/alarm.png'))
            #self.alarm_buttons[item].move(115, index*95 + 2)
            #self.alarm_buttons[item].setIconSize(QtCore.QSize(15, 15))
            #self.alarm_buttons[item].setStyleSheet('''
            #                                  QToolButton {  border: 0; background: transparent; } 
            #                                  QToolTip    { color: #000; }
            #                                  ''')
            #self.alarm_buttons[item].setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            #self.alarm_buttons[item].setToolTip(u'Установить сигнал')
            #self.connect(self.alarm_buttons[item], QtCore.SIGNAL('clicked()'), self.toggleLoggerAction)
        
    def runCryptoCourcesThread(self):
        self.requestThread = CryptoCource(self.__crypto_currency__, self.settings.get('request_timeout'))
        self.connect(self.requestThread, QtCore.SIGNAL('complete_get_crypto_cource'), self.set_crypto_cources, QtCore.Qt.QueuedConnection)
        self.connect(self.requestThread, QtCore.SIGNAL('system_logger'), self.updateSystemLogger, QtCore.Qt.QueuedConnection)
        self.connect(self.requestThread, QtCore.SIGNAL('run_update_timer'), self.runCryptoCourcesDelayTimer, QtCore.Qt.QueuedConnection)
        self.requestThread.start()
        
    def runCryptoCourcesDelayTimer(self, timeout):
        if self.settings.get('fixed_update_period') == "1":
            need_for_sleep = int (int(self.settings.get('update_period')) * 1000)
        else:
            need_for_sleep = int(( int(self.settings.get('update_period')) - timeout ) * 1000)
            need_for_sleep = 0 if need_for_sleep < 0 else need_for_sleep

        QtCore.QTimer.singleShot(need_for_sleep, self.runCryptoCourcesThread)

    def set_crypto_cources(self, coins):
        for coin_id, coin_data in coins.items():
            coin_id_master, coin_id_slave = coin_id.split('_')

            prepare_values = {
                              'time'          : datetime.fromtimestamp(coin_data['updated']).strftime('%H:%M:%S %d-%m-%Y'),
                              'buy'           : coin_data['buy'],
                              'buy_diff'      : self.price_diff(coin_id, 'buy', coin_data['buy']),
                              'sell'          : coin_data['sell'],
                              'sell_diff'     : self.price_diff(coin_id, 'sell', coin_data['sell']),
                              'master_iso'    : self.coindata[coin_id_master]['iso'],
                              'slave_iso'     : self.coindata[coin_id_slave]['iso'],
                              'last'          : coin_data['last'],
                              'min'           : coin_data['low'],
                              'max'           : coin_data['high'],
                              'avg'           : coin_data['avg'],
                              'diff'          : (coin_data['high'] - coin_data['low']),
                              'volume_master' : int(coin_data['vol_cur']),
                              'volume_slave'  : int(coin_data['vol'])
                            }
        
            prepare_string = u'''
                              <table style="margin-left: 50px;" width="100%" height="42"> 
                                <tr>
                                  <td width="200" style="font-size: 13px; color: #bebebe;"><b>Продажа</b></td>
                                  <td style="font-size: 13px;color: #bebebe;"><b>Покупка</b></td>
                                  <td align="right" style="font-size: 9px;color: #000;">{time}</td>
                                </tr>
                                <tr>
                                  <td>
                                    <span style="font-size: 15px;"> <b>{buy}</b> </span>
                                    <span style="font-size: 12px;"> <b>{buy_diff}</b> </span>
                                  </td>
                                  <td colspan="2">
                                    <span style="font-size: 15px;"> <b>{sell}</b> </span>
                                    <span style="font-size: 12px;"> <b>{sell_diff}</b> </span>
                                  </td>
                                </tr>
                              </table>
                      
                              <table width="100%" height="16"> 
                                <tr>
                                  <td width="60" style="font-size: 9px; background: #dedede;">Цены ({slave_iso}):</td>
                                  <td align="right" style="font-size: 9px; background: #fff; color: #0857A6;">
                                      Оборот: {volume_master} {master_iso}  / {volume_slave} {slave_iso}
                                  </td>
                                </tr>
                              </table>
                      
                              <table width="100%" height="32" style="color: #fff; background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #9dd53a, stop: .5 #a1d54f, stop: .51 #80c217, stop: 1 #7cbc0a);"> 
                                <tr>
                                  <td align="center" style="font-size: 11px; margin: 10px;">Последняя</td>
                                  <td align="center" style="font-size: 11px;">Минимум</td>
                                  <td align="center" style="font-size: 11px;">Максимум</td>
                                  <td align="center" style="font-size: 11px;">Средняя</td>
                                  <td align="center" style="font-size: 11px;">Разница</td>
                                </tr>
                                <tr>
                                  <td align="center">
                                    <div style="font-size: 10px; margin: 5px;"> <b>{last}</b> </div>
                                  </td>
                                  <td align="center">
                                    <span style="font-size: 10px;"> <b>{min}</b> </span>
                                  </td>
                                  <td align="center">
                                    <span style="font-size: 10px;"> <b>{max}</b> </span>
                                  </td>
                                  <td align="center">
                                    <span style="font-size: 10px;"> <b>{avg}</b> </span>
                                  </td>
                                  <td align="center">
                                    <span style="font-size: 10px;"> <b>{diff}</b> </span>
                                  </td>
                                </tr>
                             </table>
                              '''.format(**prepare_values)
        
            label_currency = getattr(self, coin_id)
            label_currency.setText(prepare_string)
            
            self.originalPixmap = QtGui.QPixmap.grabWidget(self, QtCore.QRect(0, 0, 450, self.widget_height + 3))
            
            self.updateTime.setText(u'Обновление данных: %s' % time.strftime("%H:%M:%S %d-%m-%Y"))
        
    def price_diff(self, coin_id, operation_type, value):
        index = diff_value = ''
        
        if self.history[coin_id][operation_type]:
            index = value - self.history[coin_id][operation_type]
            
            if index > 0:
                diff_value = '<font color="green">%s</font>' % '{0:+}'.format(Decimal(index).normalize())
            elif index < 0:
                diff_value = '<font color="red">%s</font>' % '{0:+}'.format(Decimal(index).normalize())
            else:
                if self.history[coin_id]['diff_%s' % operation_type]:
                    diff_value = self.history[coin_id]['diff_%s' % operation_type]
                    
            self.history[coin_id]['diff_%s' % operation_type] = diff_value
            
        self.history[coin_id][operation_type] = value
        
        return diff_value
    
    def initProgramSettings(self):
        self.settings = Settings()
        
        self.__crypto_currency__= filter(None, [item.strip() for item in self.settings.get('crypto_currencies_list').split(',')])
        getcontext().prec       = int(self.settings.get('exp_signs'))
        self.updateTimeCounter  = int(self.settings.get('update_period'))
        
        self.widget_height      = 95 * len(self.__crypto_currency__)
        self.logger_offset      = 80 if self.settings.get('show_logger') == "1" else 0 
        
        if self.settings.get('fix_window') == '1':
            self.window_fix = self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint
        else:
            self.window_fix = self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint
            
        self.program_icon = QtGui.QIcon(QtGui.QPixmap('resources/btc.png'))
        
        self.coindata = {
                'btc' : { 'title' : 'Bitcoin (BTC)',  'iso' : 'BTC', 'description' : u'Биткоин - (битка, бит, биток), первенец и глава всем криптовалютам.' },
                'ltc' : { 'title' : 'Litecoin (LTC)', 'iso' : 'LTC', 'description' : u'Лайткоин - (лайт, лайтик), вторая криптовалюта после биткоина.' },
                'usd' : { 'title' : u'Доллар (USD)',  'iso' : 'USD', 'description' : u'Доллар (бакс, убитый енот, у.е.).' },
                'eur' : { 'title' : 'Euro (EUR)',     'iso' : 'EUR', 'description' : u'Евро. Официальная валюта «еврозоны»' },
                'rur' : { 'title' : u'Рубль (RUR)',   'iso' : 'RUR', 'description' : u'Рубль (деревянный).  Денежная единица Российской Федерации' },
                'nmc' : { 'title' : 'Namecoin (NMC)', 'iso' : 'NMC', 'description' : u'Неймкоин (неймы).' },
                'nvc' : { 'title' : 'Novacoin (NVC)', 'iso' : 'NVC', 'description' : u'Новакоин (нова)' },
                'trc' : { 'title' : 'Terracoin (TRC)','iso' : 'TRC', 'description' : u'Терракоин (тараканы, терра)' },
                'ppc' : { 'title' : 'Peercoin (PPC)', 'iso' : 'PPC', 'description' : u'Пиркоин (пиры, пипцы)' },
                'ftc' : { 'title' : 'Feathercoin (FTC)', 'iso' : 'FTC', 'description' : u'(перья)' },
                'xpm' : { 'title' : 'Primecoin (XPM)',   'iso' : 'XPM', 'description' : u'Праймкоин' },
               }

    def cryptoCoinInfo(self, coin_from, coin_to):     
        prepared = [
                    self.coindata[coin_from]['title'] + ' -> ' + self.coindata[coin_to]['title'],
                    self.coindata[coin_from]['title'],
                    self.coindata[coin_from]['description'],
                    self.coindata[coin_to]['title'],
                    self.coindata[coin_to]['description']     
                   ]
        
        return u'<h4>%s</h4><b>%s</b><br/> %s <br/> <b>%s</b><br/>%s'  % tuple(prepared)
       
    def initializeSystemTray(self):
        self.quitAction = QtGui.QAction(u"Выход", self)
        self.connect(self.quitAction, QtCore.SIGNAL('triggered()'), QtGui.qApp, QtCore.SLOT('quit()'))
        
        self.sysTrayMenu = QtGui.QMenu(self) 
        self.sysTrayMenu.addAction(self.quitAction) 
        
        self.sysTrayIcon = QtGui.QSystemTrayIcon(self)
        self.sysTrayIcon.setIcon(self.program_icon) 
        self.sysTrayIcon.setVisible(True)
        self.sysTrayIcon.setContextMenu(self.sysTrayMenu) 
        self.sysTrayIcon.setToolTip(__version__)
        self.connect(self.sysTrayIcon, QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), self.sysTrayIconClicked)
        
    def sysTrayIconClicked(self, reason):
        if reason == self.sysTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.showNormal()
            
    def updateSystemLogger(self, value):
        if self.settings.get('show_logger') == '1':
            self.systemLogger.append(value)
            verticalScrollBar = self.systemLogger.verticalScrollBar()
            verticalScrollBar.setValue(verticalScrollBar.maximum())
        
    def takeScreenshot(self):
        img_format = 'png'
        initialPath = QtCore.QDir.currentPath() + "/cources_%s.%s" % (time.strftime("%H-%M-%S_-_%d-%m-%Y"), img_format)

        fileName = QtGui.QFileDialog.getSaveFileName(self, "Save As",
                initialPath,
                "%s Files (*.%s);;All Files (*)" % (img_format.upper(), img_format))
        if fileName:
            self.originalPixmap.save(fileName, img_format)
            
    def toggleLoggerAction(self):
        if self.settings.get('show_logger') == '1':
            self.settings.set('show_logger', '0')
            self.logger_offset = 0
            self.systemLogger.clear()
            self.systemLogger.hide()
        else:
            self.settings.set('show_logger', '1')
            self.logger_offset = 80
            self.systemLogger.setText(u'Логгер ошибок активен')
            self.systemLogger.show()
            
        self.setFixedSize(450, self.widget_height + self.logger_offset + 20)
        
    def toggleWindowState(self):
        if self.settings.get('fix_window') == '1':
            self.settings.set('fix_window', '0')
            state = self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint
        else:
            self.settings.set('fix_window', '1')
            state = self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint
            
        self.setWindowFlags(state)
        self.show()

        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    rendering = Program()
    rendering.setStyleSheet(''' 
                              background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0.5 #dedede, stop: 1 #bebebe);
                            ''')
    rendering.show()
    sys.exit(app.exec_())

