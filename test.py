import configparser
from splinter import Browser
from time import sleep
import traceback
import sys

class Huoche:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        # 浏览器驱动名称
        self.driver_name = 'chrome'
        # 用户名和密码
        self.username = config.get('login', 'username')
        self.passwd = config.get('login', 'password')
        # 出发地、目的地和出发日期
        self.starts = config.get('travel','starts')
        self.ends = config.get('travel', 'ends')
        self.dtime = config.get('travel', 'dtime')
        # 车次选择
        self.order = int(config.get('travel', 'order'))
        # 乘客姓名列表
        self.users = config.get('travel', 'users').split(',')
        # 席位类型和票种
        self.xb = config.get('travel', 'xb')
        self.pz = config.get('travel', 'pz')
        # 12306相关网址
        self.ticket_url = "https://kyfw.12306.cn/otn/leftTicket/init"
        self.login_url = "https://kyfw.12306.cn/otn/login/init"
        self.initmy_url = "https://kyfw.12306.cn/otn/index/initMy12306"
        self.buy_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"

    def login(self):
        try:
            # 打开登录页面
            self.driver.visit(self.login_url)
            # 填充用户名和密码
            self.driver.fill("loginUserDTO.user_name", self.username)
            self.driver.fill("userDTO.password", self.passwd)
            print("等待验证码，自行输入...")
            # 等待用户输入验证码并登录成功
            while self.driver.url!= self.initmy_url:
                sleep(1)
        except Exception as e:
            print(f"登录时出现错误: {e}")
            traceback.print_exc()

    def start(self):
        try:
            # 初始化浏览器
            self.driver = Browser(self.driver_name)
            self.driver.driver.set_window_size(1400, 1000)
            # 执行登录操作
            self.login()
            # 打开车票查询页面
            self.driver.visit(self.ticket_url)
            print("购票页面开始...")
            # 添加查询信息的cookies
            self.driver.cookies.add({"_jc_save_fromStation": self.starts})
            self.driver.cookies.add({"_jc_save_toStation": self.ends})
            self.driver.cookies.add({"_jc_save_fromDate": self.dtime})
            # 刷新页面使cookies生效
            self.driver.reload()

            count = 0
            if self.order!= 0:
                while self.driver.url == self.ticket_url:
                    # 点击查询按钮
                    self.driver.find_by_text("查询").click()
                    count += 1
                    print(f"循环点击查询... 第 {count} 次")
                    try:
                        # 点击指定车次的预订按钮
                        self.driver.find_by_text("预订")[self.order - 1].click()
                        break
                    except IndexError:
                        print("指定车次的预订按钮未找到，继续查询")
                    except Exception as e:
                        print(f"查询时出现错误: {e}")
            else:
                while self.driver.url == self.ticket_url:
                    # 点击查询按钮
                    self.driver.find_by_text("查询").click()
                    count += 1
                    print(f"循环点击查询... 第 {count} 次")
                    try:
                        # 依次点击所有预订按钮
                        for i in self.driver.find_by_text("预订"):
                            i.click()
                            sleep(1)
                            if self.driver.url!= self.ticket_url:
                                break
                    except Exception as e:
                        print(f"查询时出现错误: {e}")

            print("开始预订...")
            sleep(1)
            print('开始选择用户...')
            for user in self.users:
                try:
                    # 选择乘客
                    self.driver.find_by_text(user).last.click()
                except Exception as e:
                    print(f"选择乘客 {user} 时出现错误: {e}")

            print("提交订单...")
            sleep(1)
            try:
                # 提交订单
                self.driver.find_by_id('submitOrder_id').click()
            except Exception as e:
                print(f"提交订单时出现错误: {e}")

            sleep(1.5)
            print("确认选座...")
            try:
                # 确认选座
                self.driver.find_by_id('qr_submit_id').click()
            except Exception as e:
                print(f"确认选座时出现错误: {e}")
        except Exception as e:
            print(f"购票过程中出现错误: {e}")
            traceback.print_exc()
        finally:
            # 关闭浏览器
            self.driver.quit()

if __name__ == '__main__':
    # 创建购票对象并开始购票流程
    train_ticket = Huoche()
    train_ticket.start()
