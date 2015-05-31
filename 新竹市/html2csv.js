import request from 'request'
import cheerio from 'cheerio'
import Promise from 'bluebird'
import fs from 'fs'
import _ from 'lodash'
import stringify from 'csv-stringify'

// 動物編號,進所日期,捕捉地點,進所原因,動物性別,動物毛色,動物品種,動物體型,是否結紮,晶片號碼,棄養原因,動物紀錄,收容籠位,處理結果,圖片
const title = [['動物編號', '動物別', '動物性別', '動物品種', '動物年齡', '動物體型', '動物體重', '是否結紮', '施打疫苗', '晶片號碼', '犬牌號碼', '進所日期', '日期', '圖片']];

function generateURL() {
  return new Promise((resolve, reject)=> {
    var urls = ['http://puppy.hccg.gov.tw/?cn-i-1.html'];
    request.get(urls[0], (err, res, body)=> {
      if(err) return reject(err);
      var $ = cheerio.load(body);
      var last = $($('.fengye > table > tr > td > a').get(11)).attr('href').match(/^\.\/\?cn-i-(\d+)\.html$/)[1];
      for(var i=2;i<=last;i ++) urls.push(`http://puppy.hccg.gov.tw/?cn-i-${i}.html`);
      return resolve(urls);
    });
  });
}

function collectURL(url) {
  return new Promise((resolve, reject)=> {
    request.get(url, (err, res, body)=> {
      if(err) return reject(err);
      var $ = cheerio.load(body);
      var urls = $('.sayyes > a')
        .map((i, e)=> "http://puppy.hccg.gov.tw/" + $(e).attr('href').split('./')[1])
        .toArray();
      return resolve(urls);
    });
  });
}


function fetchInfo(url) {
  return new Promise((resolve, reject)=> {
    request.get(url, (err, res, body)=> {
      if(err) return reject(err);
      var $ = cheerio.load(body);
      var img_src = "http://puppy.hccg.gov.tw/" +$('.luoboimg').attr('src');
      var id = $('.msg_list > dt').text().split(/[：:]/)[1];
      var info = $('.msg_list > dd')
        .filter((i, e) => { if($(e).text().match(/[：:]/)) return true })
        .map((i, e) => $(e).text().split(/[：:]/)[1])
        .toArray();
      return resolve([id].concat(info).concat([img_src]));
    });
  });
}

function fetchImage(url) {
  var file_name = url.split('/')[4]
  request.get(url).pipe(fs.createWriteStream(`images/${file_name}`));
}

generateURL().then((urls)=> {
  Promise.map(urls, collectURL)
    .then((all_urls)=> {
      var all_urls = _.flatten(all_urls).slice(0, 100);
      return Promise.map(_.flatten(all_urls), fetchInfo)})
    .then((info)=> {
      info.map((i)=> fetchImage(i[13]))
      stringify(title.concat(info), (err, output) => {
        fs.writeFileSync('all.csv', output);
      })
    })
});
