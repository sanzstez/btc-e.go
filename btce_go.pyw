#-*- coding: UTF-8 -*-

from PyQt4 import QtGui, QtCore
import pyaudio, wave
import sys, urllib2, socket, ssl, httplib, json, time
from datetime import datetime
from decimal import *
from ConfigParser import SafeConfigParser

__version__ = 'BTC-E Go! 1.3.0'

####################################### 

class Settings:
    def __init__(self):
        self.filename = 'settings.ini'
        self.cfgParser = SafeConfigParser()
        self.cfgParser.read(self.filename)
        
    def get(self, key):
        return self.cfgParser.get('settings', key)
    
    def get_bool(self, key):
        return self.cfgParser.getboolean('settings', key)
    
    def set(self, key, value):
        self.cfgParser.set('settings', key, str(value) )
        self.save()
    
    def save(self):
        with open(self.filename, 'wb') as config:
            self.cfgParser.write(config)

#######################################      
    
class AlarmSettings:
    def __init__(self):
        self.filename = 'alarms.ini'
        self.cfgParser = SafeConfigParser()
        self.cfgParser.read(self.filename)
        
    def has_section(self, section_key):
        return True if self.cfgParser.has_section(section_key) else False
     
    def get(self, key):
        self.alarm_values = {
                              'max_buy_value' : 0, 'max_buy_active' : False,
                              'min_buy_value' : 0, 'min_buy_active' : False
                             }
        
        if self.has_section(key):
            self.alarm_values = {
                                 'max_buy_value'  : self.cfgParser.getfloat(key, 'max_buy_value'),
                                 'max_buy_active' : self.cfgParser.getboolean(key, 'max_buy_active'),
                                 'min_buy_value'  : self.cfgParser.getfloat(key, 'min_buy_value'),
                                 'min_buy_active' : self.cfgParser.getboolean(key, 'min_buy_active')
                                 }
            
        return self.alarm_values
       
    def set(self, section_key, section_values):
        if not self.has_section(section_key):
            self.cfgParser.add_section(section_key)
            
        for key, value in section_values.items():
            self.cfgParser.set(section_key, key, str(value) )

        self.save()
    
    def save(self):
        with open(self.filename, 'wb') as config:
            self.cfgParser.write(config)
   
####################################### 
      
class AlarmSettingsPage(QtGui.QDialog):
    def __init__(self, coin_id, parent):
        super(AlarmSettingsPage, self).__init__(parent)
        
        self.coin_id        = coin_id
        self.parent         = parent
        self.alarmSettings  = parent.alarms
        self.alarmSignals   = self.alarmSettings.get(self.coin_id)
        self.coin_master, self.coin_slave = map(str.upper, self.coin_id.split('_'))
        
        self.setFixedSize(350, 200)
        self.setWindowTitle(__version__)
        
        self.settingsViewList()
        
        self.setStyleSheet('background: none;')

    def settingsViewList(self):
        title = QtGui.QLabel(u'<b>Установить сигнал для курса %s -> %s</b>' % (self.coin_master, self.coin_slave), self )
        
        save = QtGui.QPushButton(u'Сохранить', self)
        self.connect(save, QtCore.SIGNAL('clicked()'), self.saveAlarm)
        
        cancel = QtGui.QPushButton(u'Отмена', self)
        self.connect(cancel, QtCore.SIGNAL('clicked()'), self.close)
        
        max_buy_box_group = QtGui.QGroupBox(u'Цена для сигнала максимума, %s:' % self.coin_slave)
        min_buy_box_group = QtGui.QGroupBox(u'Цена для сигнала минимума, %s:'  % self.coin_slave)
        
        self.max_buy_active_checkbox = QtGui.QCheckBox(u'Активен')
        self.max_buy_active_checkbox.setChecked(self.alarmSignals['max_buy_active'])
        
        self.max_buy_value_spinbox   = QtGui.QDoubleSpinBox()
        self.max_buy_value_spinbox.setRange(0.0, 100000.0)
        self.max_buy_value_spinbox.setDecimals(7)
        self.max_buy_value_spinbox.setValue(self.alarmSignals['max_buy_value'])
        self.max_buy_value_spinbox.setStyleSheet('height: 30px; font-size: 14px;')

        self.min_buy_active_checkbox = QtGui.QCheckBox(u'Активен')
        self.min_buy_active_checkbox.setChecked(self.alarmSignals['min_buy_active'])
        
        self.min_buy_value_spinbox   = QtGui.QDoubleSpinBox()
        self.min_buy_value_spinbox.setRange(0.0, 100000.0)
        self.min_buy_value_spinbox.setDecimals(7)
        self.min_buy_value_spinbox.setValue(self.alarmSignals['min_buy_value'])
        self.min_buy_value_spinbox.setStyleSheet('height: 30px; font-size: 14px;')

        max_buy_box = QtGui.QHBoxLayout()
        max_buy_box.addWidget(self.max_buy_value_spinbox)
        max_buy_box.addWidget(self.max_buy_active_checkbox)
        
        min_buy_box = QtGui.QHBoxLayout()
        min_buy_box.addWidget(self.min_buy_value_spinbox)
        min_buy_box.addWidget(self.min_buy_active_checkbox)
        
        control_box = QtGui.QHBoxLayout()
        control_box.addWidget(save)
        control_box.addWidget(cancel)
        
        max_buy_box_group.setLayout(max_buy_box)
        min_buy_box_group.setLayout(min_buy_box)
        
        spinBoxLayout = QtGui.QVBoxLayout()
        spinBoxLayout.addWidget(title)
        spinBoxLayout.addWidget(max_buy_box_group)
        spinBoxLayout.addWidget(min_buy_box_group)
        spinBoxLayout.addLayout(control_box)
        
        self.setLayout(spinBoxLayout)
        
    def saveAlarm(self):
        if self.max_buy_value_spinbox.value() > self.min_buy_value_spinbox.value():
            alarm_values = {
                            'max_buy_value'  : self.max_buy_value_spinbox.value(),
                            'max_buy_active' : self.max_buy_active_checkbox.isChecked(),
                            'min_buy_value'  : self.min_buy_value_spinbox.value(),
                            'min_buy_active' : self.min_buy_active_checkbox.isChecked()
                            }
        
            self.alarmSettings.set(self.coin_id, alarm_values)
            self.parent.alarm_buttons[self.coin_id].setToolTip(self.parent.get_armed_alarms(self.coin_id))
            
            self.close()
        else:
            QtGui.QMessageBox.information(self, u'Неправильно заданы параметры', 
                                          u'Значение максимума должно быть больше значения минимума')

####################################### 
        
class PlayAlarm(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)

        self.CHUNK    = 1024
        self.WAV_FILE =  wave.open('resources/ding.wav', 'rb')
        
    def run(self):
        p = pyaudio.PyAudio()

        stream = p.open(format = p.get_format_from_width(self.WAV_FILE.getsampwidth()),
                        channels = self.WAV_FILE.getnchannels(),
                        rate = self.WAV_FILE.getframerate(),
                        output = True)

        data = self.WAV_FILE.readframes(self.CHUNK)

        while data != '':
            stream.write(data)
            data = self.WAV_FILE.readframes(self.CHUNK)

        stream.stop_stream()
        stream.close()

        p.terminate()
        
####################################### 
        
class About(QtGui.QDialog):
    def __init__(self, parent=None):
        super(About, self).__init__(parent)
        
        self.setFixedSize(550, 400)
        self.setWindowTitle(__version__)
        
        self.pageContent()

    def pageContent(self):
        content = QtGui.QLabel(self)
        content.setText(u'''<div align="center" style="font-size: 12px;">
                                Программа для мониторинга состояния цен биржи BTC-E.com<br/>
                                Разработано для всех, кто знает что такое криптовалюта =)<br/><br/>
                                <b>Программа и исходный код распространяются бесплатно.</b> <br/>
                            </div>
                            
                            <div align="left" style="font-size: 11px; margin: 5px;">
                                Любой желающий может поучаствовать в разработке программы:<br/>
                                1) Принимаем ваши пожелания и предложения. <a href="http://vk.com/btce_go">Официальная группа ВК</a> <br/>
                                2) Скачать последнюю версию и узнать новости проекта можно на <a href="http://sanzstez.github.io/btc-e.go/">странице проекта в Github</a> <br/>
                                3) ... Предлагаю поддержать разработку утилиты переводом немного денег на нижеуказанные кошельки.
                                   Это реально поможет в дальнейшем развитии программы <br/>
                            </div>
                            
                            <table width="100%" style="font-size: 11px;"> 
                              <tr>
                                  <td align="center" style="color: #00732F;"><b>Bitcoin (BTC)</b></td>
                                  <td align="center" style="color: #00732F;"><b>Litecoin (LTC)</b></td>
                              </tr>
                              <tr>
                                  <td align="center">
                                      <b>151xG1K5pUVGbvguYd2vPfBSTy66Uifoq4</b>
                                  </td>
                                  <td align="center">
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
                        ''')
        
        content.setAlignment(QtCore.Qt.AlignTop)
        content.setGeometry(QtCore.QRect(0, 10, 550, 400))
        content.setWordWrap(True)
        content.setOpenExternalLinks(True)
        content.setMargin(5)
        content.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse | QtCore.Qt.TextSelectableByKeyboard | QtCore.Qt.LinksAccessibleByMouse)
  
####################################### 
  
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
     
########################################################
        
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
        self.toggleWindowStateButton.setIcon(QtGui.QIcon(self.window_fix_icon))
        self.toggleWindowStateButton.move(367, self.widget_height)
        self.toggleWindowStateButton.setIconSize(QtCore.QSize(18, 18))
        self.toggleWindowStateButton.setStyleSheet('''
                                                    QToolButton {  border: 0; background: transparent; } 
                                                    QToolTip    { color: #000; }
                                                   ''')
        self.toggleWindowStateButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.toggleWindowStateButton.setToolTip(self.window_fix_title)
        self.connect(self.toggleWindowStateButton, QtCore.SIGNAL('clicked()'), self.toggleWindowState)
        
        self.toggleTooltipStateButton = QtGui.QToolButton(self)
        self.toggleTooltipStateButton.setIcon(QtGui.QIcon(self.tooltip_icon))
        self.toggleTooltipStateButton.move(347, self.widget_height)
        self.toggleTooltipStateButton.setIconSize(QtCore.QSize(18, 18))
        self.toggleTooltipStateButton.setStyleSheet('''
                                                    QToolButton {  border: 0; background: transparent; } 
                                                    QToolTip    { color: #000; }
                                                   ''')
        self.toggleTooltipStateButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.toggleTooltipStateButton.setToolTip(self.tooltip_title)
        self.connect(self.toggleTooltipStateButton, QtCore.SIGNAL('clicked()'), self.toggleTooltipState)
        
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
        if self.settings.get_bool('show_logger'): self.systemLogger.setVisible(True)
        
        self.updateTime = QtGui.QLabel(self)
        self.updateTime.setGeometry(QtCore.QRect(3, self.widget_height, 340, 20))
        self.updateTime.setStyleSheet('background: transparent; font-weight: bold; font-size: 11px;')
        
        self.originalPixmap = None
        self.originalPixmap = QtGui.QPixmap.grabWidget(self, QtCore.QRect(0, 0, 450, self.widget_height + 3))  
        
    def initHistoryStack(self):
        self.price_history, self.alarm_history = {},{}
        
        for coin in self.__crypto_currency__:
            self.price_history[coin] = {'buy' : None, 'sell' : None, 'diff_buy' : None, 'diff_sell' : None}
            self.alarm_history[coin] = {'max_buy' : False, 'min_buy' : False}
  
    def initCryptoCourcesView(self):
        self.alarm_buttons = {}
        
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

            self.alarm_buttons[item] = QtGui.QToolButton(self)
            self.alarm_buttons[item].setIcon(QtGui.QIcon('resources/alarm.png'))
            self.alarm_buttons[item].move(0, index*95 + 78)
            self.alarm_buttons[item].setIconSize(QtCore.QSize(15, 15))
            self.alarm_buttons[item].setStyleSheet('''
                                                    QToolButton {  border: 0; background: transparent; } 
                                                    QToolTip    { color: #000; }
                                                   ''')
            self.alarm_buttons[item].setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.alarm_buttons[item].setToolTip(self.get_armed_alarms(item))
            self.connect(self.alarm_buttons[item], QtCore.SIGNAL('clicked()'), lambda value = item: self.set_alarm_signal(value))
        
    def runCryptoCourcesThread(self):
        self.requestThread = CryptoCource(self.__crypto_currency__, self.settings.get('request_timeout'))
        self.connect(self.requestThread, QtCore.SIGNAL('complete_get_crypto_cource'), self.set_crypto_cources, QtCore.Qt.QueuedConnection)
        self.connect(self.requestThread, QtCore.SIGNAL('system_logger'), self.updateSystemLogger, QtCore.Qt.QueuedConnection)
        self.connect(self.requestThread, QtCore.SIGNAL('run_update_timer'), self.runCryptoCourcesDelayTimer, QtCore.Qt.QueuedConnection)
        self.requestThread.start()
        
    def runCryptoCourcesDelayTimer(self, timeout):
        if self.settings.get_bool('fixed_update_period'):
            need_for_sleep = int (int(self.settings.get('update_period')) * 1000)
        else:
            need_for_sleep = int(( int(self.settings.get('update_period')) - timeout ) * 1000)
            need_for_sleep = 0 if need_for_sleep < 0 else need_for_sleep

        QtCore.QTimer.singleShot(need_for_sleep, self.runCryptoCourcesThread)

    def set_crypto_cources(self, coins):
        if coins:
            first_currency_price = coins[self.__crypto_currency__[0]]['buy'] if self.__crypto_currency__ else None
            self.setWindowTitle(u'[%s] %s' % (first_currency_price, __version__))
        
        for coin_id, coin_data in coins.items():
            coin_id_master, coin_id_slave = coin_id.split('_')

            self.__crypto_currency__

            prepare_values = {
                              'time'          : datetime.fromtimestamp(coin_data['updated']).strftime('%H:%M:%S %d-%m-%Y'),
                              'buy'           : self.alarm_processing(coin_id, coin_data['buy']),
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
            
            self.notify_processing(coin_id)
            
    def set_alarm_signal(self, coin_id):
        self.alarm_settings = AlarmSettingsPage(coin_id, self)
        self.alarm_settings.show()   
        
    def notify_processing(self, coin_id):
        thresholds = []
        
        if self.signal_active:
            if self.settings.get_bool('show_tooltip'):
                for coin_id, alarm in self.alarm_history.items():
                    coin_master, coin_slave = map(str.upper, coin_id.split('_'))
                
                    if alarm['max_buy']:
                        thresholds.append(u'Максимум %s -> %s: %s %s' % (coin_master, coin_slave, self.price_history[coin_id]['buy'], coin_slave))
                
                    if alarm['min_buy']:
                        thresholds.append(u'Минимум %s -> %s: %s %s' % (coin_master, coin_slave, self.price_history[coin_id]['buy'], coin_slave))       
                
                self.sysTrayIcon.showMessage(u'Превышены границы курса', '\n'.join(thresholds), QtGui.QSystemTrayIcon.Information, 15000)
            
            self.alarm_sound = PlayAlarm()
            self.alarm_sound.start()
            
        self.signal_active = False
            
    def alarm_processing(self, coin_id, value):
        options = self.alarms.get(coin_id)
        price   = value
        
        if options['max_buy_active']:
            if value >= options['max_buy_value']:
                price = '<font color="green">%s</font>' % value
                if not self.alarm_history[coin_id]['max_buy']:
                    self.signal_active = self.alarm_history[coin_id]['max_buy'] = True
            else:
                self.alarm_history[coin_id]['max_buy'] = False
  
        if options['min_buy_active']:
            if value <= options['min_buy_value']:
                price = '<font color="red">%s</font>' % value
                if not self.alarm_history[coin_id]['min_buy']:
                    self.signal_active = self.alarm_history[coin_id]['min_buy'] = True
            else:
                self.alarm_history[coin_id]['min_buy'] = False
        
        return price
    
    def get_armed_alarms(self, coin_id):
        options = self.alarms.get(coin_id)
        coin_slave = map(str.upper, coin_id.split('_'))[1]
        thresholds = []

        if options['max_buy_active']:
            thresholds.append(u'MAX: <b>%s %s</b>' % (options['max_buy_value'], coin_slave))
                
        if options['min_buy_active']:
            thresholds.append(u'MIN: <b>%s %s</b>' % (options['min_buy_value'], coin_slave))       
          
        return '<br/>'.join(thresholds) if thresholds else u'Установить сигнал'
        
    def price_diff(self, coin_id, operation_type, value):
        diff_price = ''

        if self.price_history[coin_id][operation_type]:
            index = value - self.price_history[coin_id][operation_type]
            
            if index > 0:
                diff_price = '<font color="green">%s</font>' % '{0:+}'.format(Decimal(index).normalize())
            elif index < 0:
                diff_price = '<font color="red">%s</font>' % '{0:+}'.format(Decimal(index).normalize())
            else:
                if self.price_history[coin_id]['diff_%s' % operation_type]:
                    diff_price = self.price_history[coin_id]['diff_%s' % operation_type]
                    
            self.price_history[coin_id]['diff_%s' % operation_type] = diff_price
            
        self.price_history[coin_id][operation_type] = value
        
        return diff_price
    
    def initProgramSettings(self):
        self.settings = Settings()
        self.alarms   = AlarmSettings()

        self.__crypto_currency__= filter(None, [item.strip() for item in self.settings.get('crypto_currencies_list').split(',')])
        getcontext().prec       = int(self.settings.get('exp_signs'))
        self.updateTimeCounter  = int(self.settings.get('update_period'))
        
        self.widget_height      = 95 * len(self.__crypto_currency__)
        self.logger_offset      = 80 if self.settings.get_bool('show_logger') else 0
        self.signal_active      = False
        
        self.program_icon = QtGui.QIcon(QtGui.QPixmap('resources/btc.png'))
        self.fix_window(self.settings.get_bool('fixed_window'))
        self.show_tooltip(self.settings.get_bool('show_tooltip'))
            
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

    def cryptoCoinInfo(self, coin_master, coin_slave):     
        prepared = [
                    self.coindata[coin_master]['title'] + ' -> ' + self.coindata[coin_slave]['title'],
                    self.coindata[coin_master]['title'],
                    self.coindata[coin_master]['description'],
                    self.coindata[coin_slave]['title'],
                    self.coindata[coin_slave]['description']     
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
        if self.settings.get_bool('show_logger'):
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
        if self.settings.get_bool('show_logger'):
            self.settings.set('show_logger', False)
            self.logger_offset = 0
            self.systemLogger.clear()
            self.systemLogger.hide()
        else:
            self.settings.set('show_logger', True)
            self.logger_offset = 80
            self.systemLogger.setText(u'Логгер ошибок активен')
            self.systemLogger.show()
            
        self.setFixedSize(450, self.widget_height + self.logger_offset + 20)
        
    def toggleWindowState(self):
        if self.settings.get_bool('fixed_window'):
            self.settings.set('fixed_window', False)
            self.fix_window(False)
        else:
            self.settings.set('fixed_window', True)
            self.fix_window(True)
            
        self.toggleWindowStateButton.setIcon(QtGui.QIcon(self.window_fix_icon))
        self.toggleWindowStateButton.setToolTip(self.window_fix_title)
            
        self.setWindowFlags(self.window_fix)
        self.show()
        
    def fix_window(self, state):
        if state:
            self.window_fix = self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint
            self.window_fix_icon  = 'resources/unfixed.png'
            self.window_fix_title = u'Не показывать поверх всех окон'
        else:
            self.window_fix = self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint
            self.window_fix_icon  = 'resources/fixed.png'
            self.window_fix_title = u'Показывать поверх всех окон'
            
    def toggleTooltipState(self):
        if self.settings.get_bool('show_tooltip'):
            self.settings.set('show_tooltip', False)
            self.show_tooltip(False)
        else:
            self.settings.set('show_tooltip', True)
            self.show_tooltip(True)
            
        self.toggleTooltipStateButton.setIcon(QtGui.QIcon(self.tooltip_icon))
        self.toggleTooltipStateButton.setToolTip(self.tooltip_title)
        
    def show_tooltip(self, state):
        if state:
            self.tooltip_icon  = 'resources/hide_tooltip.png'
            self.tooltip_title = u'Отключить всплывающие сообщения'
        else:
            self.tooltip_icon  = 'resources/show_tooltip.png'
            self.tooltip_title = u'Включить всплывающие сообщения'
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    rendering = Program()
    rendering.setStyleSheet(''' 
                              background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0.5 #dedede, stop: 1 #bebebe);
                            ''')
    rendering.show()
    sys.exit(app.exec_())

