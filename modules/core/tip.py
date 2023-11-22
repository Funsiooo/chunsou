# -*- coding: utf-8 -*-

'''
@File    ：tip.py
@IDE     ：PyCharm
@Author  ：Funsiooo
@Github  ：https://github.com/Funsiooo
'''


from tabulate import tabulate
from modules.core.output import tip_start
def tips():
    fofa_table_data = [
        ["例句", "用途说明", "注"],
        ["title=\"beijing\"", "从标题中搜索“北京”", "-"],
        ["header=\"elastic\"", "从http头中搜索“elastic”", "-"],
        ["body=\"网络空间测绘\"", "从html正文中搜索“网络空间测绘”", "-"],
        ["fid=\"sSXXGNUO2FefBTcCLIT/2Q==\"", "查找相同的网站指纹", "搜索网站类型资产"],
        ["domain=\"qq.com\"", "搜索根域名带有qq.com的网站", "-"],
        ["icp=\"京ICP证030173号\"", "查找备案号为“京ICP证030173号”的网站", "搜索网站类型资产"],
        ["js_name=\"js/jquery.js\"", "查找网站正文中包含js/jquery.js的资产", "搜索网站类型资产"],
        ["js_md5=\"82ac3f14327a8b7ba49baa208d4eaa15\"", "查找js源码与之匹配的资产", "-"],
        ["cname=\"ap21.inst.siteforce.com\"", "查找cname为\"ap21.inst.siteforce.com\"的网站", "-"],
        ["cname_domain=\"siteforce.com\"", "查找cname包含“siteforce.com”的网站", "-"],
        ["cloud_name=\"Aliyundun\"", "通过云服务名称搜索资产", "-"],
        ["product=\"NGINX\"", "搜索此产品的资产", "个人版及以上可用"],
        ["category=\"服务\"", "搜索此产品分类的资产", "个人版及以上可用"],
        ["sdk_hash==\"Mkb4Ms4R96glv/T6TRzwPWh3UDatBqeF\"", "搜索使用此sdk的资产", "商业版及以上可用"],
        ["icon_hash=\"-247388890\"", "搜索使用此 icon 的资产", "-"],
        ["host=\".gov.cn\"", "从url中搜索”.gov.cn”", "搜索要用host作为名称"],
        ["port=\"6379\"", "查找对应“6379”端口的资产", "-"],
        ["ip=\"1.1.1.1\"", "从ip中搜索包含“1.1.1.1”的网站", "搜索要用ip作为名称"],
        ["ip=\"220.181.111.1/24\"", "查询IP为“220.181.111.1”的C网段资产", "-"],
        ["status_code=\"402\"", "查询服务器状态为“402”的资产", "查询网站类型数据"],
        ["protocol=\"quic\"", "查询quic协议资产", "搜索指定协议类型(在开启端口扫描的情况下有效)"],
        ["country=\"CN\"", "搜索指定国家(编码)的资产", "-"],
        ["region=\"Xinjiang Uyghur Autonomous Region\"", "搜索指定行政区的资产", "-"],
        ["city=\"Ürümqi\"", "搜索指定城市的资产", "-"],
        ["cert=\"baidu\"", "搜索证书(https或者imaps等)中带有baidu的资产", "-"],
        ["cert.subject=\"Oracle Corporation\"", "搜索证书持有者是Oracle Corporation的资产", "-"],
        ["cert.issuer=\"DigiCert\"", "搜索证书颁发者为DigiCert Inc的资产", "-"],
        ["cert.is_valid=true", "验证证书是否有效，true有效，false无效", "个人版及以上可用"],
        ["cert.is_match=true", "证书和域名是否匹配；true匹配、false不匹配", "个人版及以上可用"],
        ["cert.is_expired=false", "证书是否过期；true过期、false未过期", "个人版及以上可用"],
        ["jarm=\"2ad...83e81\"", "搜索JARM指纹", "-"],
        ["banner=\"users\" && protocol=\"ftp\"", "搜索JARM指纹", "-"],
        ["type=\"service\"", "搜索所有协议资产，支持subdomain和service两种", "搜索所有协议资产"],
        ["os=\"centos\"", "搜索CentOS资产", "-"],
        ["server==\"Microsoft-IIS/10\"", "搜索IIS 10服务器", "-"],
        ["app=\"Microsoft-Exchange\"", "搜索Microsoft-Exchange设备", "-"],
        ["after=\"2017\" && before=\"2017-10-01\"", "时间范围段搜索", "-"],
        ["asn=\"19551\"", "搜索指定asn的资产", "-"],
        ["org=\"LLC Baxet\"", "搜索指定org(组织)的资产", "-"],
        ["base_protocol=\"udp\"", "搜索指定udp协议的资产", "-"],
        ["is_fraud=false", "排除仿冒/欺诈数据", "专业版及以上可用"],
        ["is_honeypot=false", "排除蜜罐数据", "专业版及以上可用"],
        ["is_ipv6=true", "搜索ipv6的资产", "搜索ipv6的资产,只接受true和false"],
        ["is_domain=true", "搜索域名的资产", "搜索域名的资产,只接受true和false"],
        ["is_cloud=true", "筛选使用了云服务的资产", "-"]
    ]

    hunter_table_data = [
        ["例句", "用途说明", "注"],
        ["ip=\"1.1.1.1\"", "搜索IP为 ”1.1.1.1”的资产"],
        ["ip=\"220.181.111.0/24\"", "搜索网段为\"220.181.111.0\"的C段资产"],
        ["ip.port=\"80\"", "搜索开放端口为”80“的资产"],
        ["ip.country=\"CN\" 或 ip.country=\"中国\"", "搜索IP对应主机所在国为”中国“的资产"],
        ["iip.province=\"江苏\"", "搜索IP对应主机在江苏省的资产"],
        ["ip.city=\"北京\"", "搜索IP对应主机所在城市为”北京“市的资产"],
        ["ip.isp=\"电信\"", "搜索运营商为”中国电信”的资产"],
        ["ip.os=\"Windows\"", "搜索操作系统标记为”Windows“的资产"],
        ["app=\"Hikvision 海康威视 Firmware 5.0+\" && ip.ports=\"8000\"", "搜索操作系统标记为”Windows“的资产"],
        ["ip.port_count>\"2\"", "搜索开放端口大于2的IP（支持等于、大于、小于）"],
        ["domain=\"qianxin.com\"", "搜索域名包含\"qianxin.com\"的网站"],
        ["domain.suffix=\"qianxin.com\"", "搜索主域为\"qianxin.com\"的网站"],
        ["domain.dns_type=\"mx\"", "搜索关联\"MX\"解析记录的资产(查看枚举值)"],
        ["domain.status=\"clientDeleteProhibited\"", "搜索域名状态\"client Delete Prohibited\"的网站(查看枚举值)"],
        ["domain.whois_server=\"whois.markmonitor.com\"", "搜索whois服务器为\"whois.markmonitor.com\"的网站"],
        ["domain.name_server=\"ns1.qq.com\"", "搜索名称服务器为\"ns1.qq.com\"的网站"],
        ["domain.name_server=\"ns1.qq.com\"", "搜索名称服务器为\"ns1.qq.com\"的网站"],
        ["header.server==\"Microsoft-IIS/10\"", "搜索server全名为“Microsoft-IIS/10”的服务器"],
        ["header.content_length=\"691\"", "搜索HTTP消息主体的大小为691的网站"],
        ["header.status_code=\"402\"", "搜索HTTP请求返回状态码为”402”的资产"],
        ["header=\"elastic\"", "搜索HTTP请求头中含有”elastic“的资产"],
        ["is_web=true", "搜索web资产"],
        ["web.title=\"北京\"", "从网站标题中搜索“北京”"],
        ["web.body=\"网络空间测绘\"", "   搜索网站正文包含”网络空间测绘“的资产"],
        ["after=\"2021-01-01\" && before=\"2021-12-31\"", "搜索2021年的资产"],
        ["web.similar=\"baidu.com:443\"", "查询与baidu.com:443网站的特征相似的资产"],
        ["web.similar_icon==\"17262739310191283300\"", "查询网站icon与该icon相似的资产"],
        ["web.icon=\"22eeab765346f14faf564a4709f98548\"", "查询网站icon与该icon相同的资产"],
        ["web.similar_id=\"3322dfb483ea6fd250b29de488969b35\"", "查询与该网页相似的资产"],
        ["web.tag=\"登录页面\"", "查询包含资产标签\"登录页面\"的资产(查看枚举值)"],
        ["icp.number=\"京ICP备16020626号-8\"", "搜索域名关联的ICP备案号为”京ICP备16020626号-8”的网站资产"],
        ["icp.web_name=\"奇安信\"", "搜索ICP备案网站名中含有“奇安信”的资产"],
        ["icp.name=\"奇安信\"", "搜索ICP备案单位名中含有“奇安信”的资产"],
        ["icp.type=\"企业\"", "搜索ICP备案主体为“企业”的资产"],
        ["icp.industry=\"软件和信息技术服务业\"", "搜索ICP备案行业为“软件和信息技术服务业”的资产(查看枚举值)"],
        ["protocol=\"http\"", "搜索协议为”http“的资产"],
        ["protocol.transport=\"udp\"", "搜索传输层协议为”udp“的资产"],
        ["protocol.banner=\"nginx\"", "查询端口响应中包含\"nginx\"的资产"],
        ["app.name=\"小米 Router\"", "搜索标记为”小米 Router“的资产"],
        ["app.type=\"开发与运维\"", "查询包含组件分类为\"开发与运维\"的资产"],
        ["app.vendor=\"PHP\"", "查询包含组件厂商为\"PHP\"的资产"],
        ["app.version=\"1.8.1\"", "查询包含组件版本为\"1.8.1\"的资产"],
        ["cert=\"baidu\"", "搜索证书中带有baidu的资产"],
        ["cert.subject=\"qianxin.com\"", "搜索证书使用者包含qianxin.com的资产"],
        ["cert.subject.suffix=\"qianxin.com\"", "搜索证书使用者为qianxin.com的资产"],
        ["cert.subject_org=\"奇安信科技集团股份有限公司\"", "搜索证书使用者组织是奇安信科技集团股份有限公司的资产"],
        ["cert.issuer=\"Let's Encrypt Authority X3\"", "搜索证书颁发者是Let's Encrypt Authority X3的资产"],
        ["cert.issuer_org=\"Let's Encrypt\"", "搜索证书颁发者组织是Let's Encrypt的资产"],
        ["cert.sha-1=\"be7605a3b72b60fcaa6c58b6896b9e2e7442ec50\"", "搜索证书签名该哈希算法sha1的资产"],
        ["cert.sha-256=\"4e529a65512029d77a28cbe694c7dad1e60f98b5cb89bf2aa329233acacc174e\"",
         "搜索证书签名该哈希算法sha256资产"],
        ["cert.sha-md5=\"aeedfb3c1c26b90d08537523bbb16bf1\"", "搜索该证书签名哈希算法shamd5的资产"],
        ["cert.serial_number=\"35351242533515273557482149369\"", "搜索证书序列号是35351242533515273557482149369的资产"],
        ["cert.is_expired=true", "搜索证书已过期的资产"],
        ["cert.is_trust=true", "搜索证书可信的资产"],
        ["vul.gev=\"GEV-2021-1075\"", "查询存在该专项漏洞的资产"],
        ["vul.cve=\"CVE-2021-2194\"", "查询存在该漏洞的资产"],
        ["vul.gev=\"GEV-2021-1075\" && vul.state=\"已修复\"", "查询存在该专项漏洞资产中，已修复漏洞的资产"],
        ["web.is_vul=true", "查询存在历史漏洞的资产"]
    ]

    # 生成表格
    # table = tabulate(table_data, headers="firstrow", tablefmt="plain")

    # table_pipe = tabulate(table_data, headers="firstrow", tablefmt="pipe")

    fofa_table_orgtbl = tabulate(fofa_table_data, headers="firstrow", tablefmt="orgtbl")
    hunter_table_orgtbl = tabulate(hunter_table_data, headers="firstrow", tablefmt="orgtbl")

    # # 自定义表格样式（调整字体颜色和样式）
    # table = colored(table, "cyan", attrs=["bold"])
    # table_plain = tabulate(table_data, headers="firstrow", tablefmt="plain")

    print('''
 ______     __                                _                                                      
|  ____|   / _|                              | |                                                     
| |__ ___ | |_ __ _   ___  ___  __ _ _ __ ___| |__     __ _ _ __ __ _ _ __ ___  _ __ ___   __ _ _ __ 
|  __/ _ \|  _/ _` | / __|/ _ \/ _` | '__/ __| '_ \   / _` | '__/ _` | '_ ` _ \| '_ ` _ \ / _` | '__|
| | | (_) | || (_| | \__ \  __/ (_| | | | (__| | | | | (_| | | | (_| | | | | | | | | | | | (_| | |   
|_|  \___/|_| \__,_| |___/\___|\__,_|_|  \___|_| |_|  \__, |_|  \__,_|_| |_| |_|_| |_| |_|\__,_|_|   
                                                       __/ |                                         
                                                      |___/                                                                          
                                                                       ''')
    print(fofa_table_orgtbl)
    print('\n')
    print('''
 _    _             _                                      _                                                      
| |  | |           | |                                    | |                                                     
| |__| |_   _ _ __ | |_ ___ _ __   ___  ___  __ _ _ __ ___| |__     __ _ _ __ __ _ _ __ ___  _ __ ___   __ _ _ __ 
|  __  | | | | '_ \| __/ _ \ '__| / __|/ _ \/ _` | '__/ __| '_ \   / _` | '__/ _` | '_ ` _ \| '_ ` _ \ / _` | '__|
| |  | | |_| | | | | ||  __/ |    \__ \  __/ (_| | | | (__| | | | | (_| | | | (_| | | | | | | | | | | | (_| | |   
|_|  |_|\__,_|_| |_|\__\___|_|    |___/\___|\__,_|_|  \___|_| |_|  \__, |_|  \__,_|_| |_| |_|_| |_| |_|\__,_|_|   
                                                                    __/ |                                         
                                                                   |___/                                      
                                                                       ''')
    print(hunter_table_orgtbl)

def tip_main():
    tip_start()
    tips()

