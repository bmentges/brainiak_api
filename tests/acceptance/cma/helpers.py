from time import sleep

def do_login(browser, user, password):
    browser.visit('http://admin.backstage.dev.globoi.com')
    sleep(2)

    browser.fill('username', user)
    browser.fill('password', password)

    button = browser.find_by_name('button')
    button.click()
