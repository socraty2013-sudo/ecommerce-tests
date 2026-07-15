class ProductPage:
    def __init__(self,page, base_url):
        self.page = page
        self.base_url =base_url

    def open_list(self):
        self.page.goto(f"{self.base_url}/")

    def open_add(self):
        self.page.goto(f"{self.base_url}/products/add")

    def add_product(self, name, price, stock):
        self.page.fill("input[name='name']", name)
        self.page.fill("input[name='price']", price)
        self.page.fill("input[name='stock']", stock)
        self.page.click("button[type='submit']")   # CSS 属性选择器里，值如果是纯字母数字（比如 submit），引号可加可不加。

    def get_product_count(self):
        # tr — 找到所有 <tr> 行
        # :has(td) — 只要包含 <td> 的行（过滤掉表头的 <th> 行）
        # .count() — Playwright 计数，返回几行
        return self.page.locator("tr:has(td)").count()

    def get_page_title(self):
        return self.page.text_content("h1")  # 找 <h1>xxx</h1>，返回 xxx