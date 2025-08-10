
import json
import datetime
import requests
import pandas as pd
import re






def is_trade_day():
    """
    判断今天是否为股票交易日
    返回: bool
    """
    # 当前时间
    now = datetime.datetime.now()
    
    # 如果是周末，不是交易日
    if now.weekday() >= 5:
        print("今天是周末")
        return False
        
    # 主要节假日（可以按年更新）
    holidays_2025 = [

        '2025-10-01', '2025-10-02', '2025-10-03', '2025-10-04',
        '2025-10-05', '2025-10-06', '2025-10-07'
    ]
    
    # 如果是节假日，不是交易日
    today = now.strftime('%Y-%m-%d')
    if today in holidays_2025:
        print("今天是节假日")
        return False
        
    # 判断是否在交易时间内
    trade_time = now.time()
    if (datetime.time(9, 30) <= trade_time <= datetime.time(11, 31) or
        datetime.time(13, 0) <= trade_time <= datetime.time(15, 1)):
        return True
    print("现在不是交易时间")
    return False




#腾讯日线
def get_price_day_tx(code, end_date='', count=10, frequency='1d'):     #日线获取  
    unit='week' if frequency in '1w' else 'month' if frequency in '1M' else 'day'     #判断日线，周线，月线
    if end_date:  end_date=end_date.strftime('%Y-%m-%d') if isinstance(end_date,datetime.date) else end_date.split(' ')[0]
    end_date='' if end_date==datetime.datetime.now().strftime('%Y-%m-%d') else end_date   #如果日期今天就变成空    
    URL=f'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},{unit},,{end_date},{count},qfq'     
    st= json.loads(requests.get(URL).content);    ms='qfq'+unit;      stk=st['data'][code]   
    buf=stk[ms] if ms in stk else stk[unit]       #指数返回不是qfqday,是day
    df=pd.DataFrame(buf,columns=['time','open','close','high','low','volume'],dtype='float')     
    df.time=pd.to_datetime(df.time);    df.set_index(['time'], inplace=True);   df.index.name=''          #处理索引 
    return df

#腾讯分钟线
def get_price_min_tx(code, end_date=None, count=10, frequency='1d'):    #分钟线获取 
    ts=int(frequency[:-1]) if frequency[:-1].isdigit() else 1           #解析K线周期数
    if end_date: end_date=end_date.strftime('%Y-%m-%d') if isinstance(end_date,datetime.date) else end_date.split(' ')[0]        
    URL=f'http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={code},m{ts},,{count}' 
    st= json.loads(requests.get(URL).content);       buf=st['data'][code]['m'+str(ts)] 
    df=pd.DataFrame(buf,columns=['time','open','close','high','low','volume','n1','n2'])   
    df=df[['time','open','close','high','low','volume']]    
    df[['open','close','high','low','volume']]=df[['open','close','high','low','volume']].astype('float')
    df.time=pd.to_datetime(df.time);   df.set_index(['time'], inplace=True);   df.index.name=''          #处理索引     
    df['close'][-1]=float(st['data'][code]['qt'][code][3])                #最新基金数据是3位的
    return df


#sina新浪全周期获取函数，分钟线 5m,15m,30m,60m  日线1d=240m   周线1w=1200m  1月=7200m
def get_price_sina(code, end_date='', count=10, frequency='60m'):    #新浪全周期获取函数    
    frequency=frequency.replace('1d','240m').replace('1w','1200m').replace('1M','7200m');   mcount=count
    ts=int(frequency[:-1]) if frequency[:-1].isdigit() else 1       #解析K线周期数
    if (end_date!='') & (frequency in ['240m','1200m','7200m']): 
        end_date=pd.to_datetime(end_date) if not isinstance(end_date,datetime.date) else end_date    #转换成datetime
        unit=4 if frequency=='1200m' else 29 if frequency=='7200m' else 1    #4,29多几个数据不影响速度
        count=count+(datetime.datetime.now()-end_date).days//unit            #结束时间到今天有多少天自然日(肯定 >交易日)        
        #print(code,end_date,count)    
    URL=f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={code}&scale={ts}&ma=5&datalen={count}' 
    dstr= json.loads(requests.get(URL).content);       
    #df=pd.DataFrame(dstr,columns=['day','open','high','low','close','volume'],dtype='float') 
    df= pd.DataFrame(dstr,columns=['day','open','high','low','close','volume'])
    df['open'] = df['open'].astype(float); df['high'] = df['high'].astype(float);                          #转换数据类型
    df['low'] = df['low'].astype(float);   df['close'] = df['close'].astype(float);  df['volume'] = df['volume'].astype(float)    
    df.day=pd.to_datetime(df.day);    df.set_index(['day'], inplace=True);     df.index.name=''            #处理索引                 
    if (end_date!='') & (frequency in ['240m','1200m','7200m']): return df[df.index<=end_date][-mcount:]   #日线带结束时间先返回              
    return df

def get_price(code, end_date='',count=10, frequency='1d', fields=[]):        #对外暴露只有唯一函数，这样对用户才是最友好的  
    xcode = code.replace('.XSHG','').replace('.XSHE','')                     #证券代码编码兼容处理 
    
    # 处理各种前缀的代码
    if 'XSHG' in code:
        xcode = 'sh' + xcode
    elif 'XSHE' in code:
        xcode = 'sz' + xcode
    elif code.startswith('bj'):
        xcode = code  # 北交所代码保持原样
    elif code.startswith('of'):
        xcode = 'sz' + code[2:] if code[2] in ['1','2'] else 'sh' + code[2:]  # 根据基金代码规则处理
    else:
        xcode = code

    if  frequency in ['1d','1w','1M']:   #1d日线  1w周线  1M月线
         try:    return get_price_sina( xcode, end_date=end_date,count=count,frequency=frequency)   #主力
         except: return get_price_day_tx(xcode,end_date=end_date,count=count,frequency=frequency)   #备用                    
    
    if  frequency in ['1m','5m','15m','30m','60m']:  #分钟线 ,1m只有腾讯接口  5分钟5m   60分钟60m
         if frequency in '1m': return get_price_min_tx(xcode,end_date=end_date,count=count,frequency=frequency)
         try:    return get_price_sina(  xcode,end_date=end_date,count=count,frequency=frequency)   #主力   
         except: return get_price_min_tx(xcode,end_date=end_date,count=count,frequency=frequency)   #备用

def get_stock_price(code):
    # 获取最近2天的股票数据
    df = get_price(code, frequency='1d', count=1)
    df2 = get_price(code, frequency='1m', count=1)
    if df is None:
        return "无法获取股票数据"
    
    # 获取今日数据
    today = df2.iloc[-1]
    # 获取昨日收盘价
    yesterday_close = df.iloc[-1]['close']
    
    # 计算涨跌幅
    change_pct = (today['close'] - yesterday_close) / yesterday_close * 100
    
    # 格式化返回信息
    result = f"{today['close']:.2f} ({change_pct:+.2f}%)"
    #result += f"最高: {today['high']:.2f} ({((today['high']-yesterday_close)/yesterday_close*100):+.2f}%)\n"
    #result += f"最低: {today['low']:.2f} ({((today['low']-yesterday_close)/yesterday_close*100):+.2f}%)"
    
    return result       


# 股票代码转换
def get_stock_info(keyword,flag=0):
    """
    通过新浪财经接口查询股票信息
    :param keyword: 股票代码或股票名称
    :return: 匹配到的股票列表
    """
    # 新浪股票搜索接口
    url = f"http://suggest3.sinajs.cn/suggest/type=&key={keyword}&name=suggestdata_1"
    
    try:
        response = requests.get(url)
        # 解析返回的文本
        content = response.text
        # 提取股票信息
        match = re.search(r'"(.*?)"', content)
        
        if match and match.group(1):
            stocks = []
            for item in match.group(1).split(';'):
                if item:
                    # 解析返回的数据
                    parts = item.split(',')
                    if len(parts) >= 4:
                        code = parts[3]
                        # 只处理8位代码
                        if len(code) == 8:
                            stock_info = {
                                'code': code,
                                'name': parts[4]
                            }
                            stocks.append(stock_info)
            return stocks
        return []

    except Exception as e:
        print(f"查询出错: {str(e)}")
        return []
    





import requests

def post_json(a,url):

    data = {
        "content": str(a)
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    requests.post(url, json=data, headers=headers)
    
    return


