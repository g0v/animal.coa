require! <[cheerio fs request]>

opt =
  album: \album/
  base: \http://www.dog.dias.com.tw
  extra:
    * \album_file
    * \animal_has_chip
    * \animal_chip_number
  fields:
    * \animal_opendate
    * \animal_found_place
    * \animal_pedigree
    * \animal_sex
    * \animal_bodytype
    * \animal_entry_reason
    * \animal_id
  url: \http://www.dog.dias.com.tw/index.php?op=announcement&page=

page 1 []

function output
  fields = opt.fields ++ opt.extra
  console.log fields * \,
  for animal in it
    console.log [animal[..] for fields] * \,

function page index, animals
  (err, res, html) <-! request opt.url + index
  throw err if err
  $ = cheerio.load html
  (img = $ '.rightBox img[width]').each !->
    animal =
      album_file: opt.base + ($_ = $ @).attr \src
      animal_chip_number: ''
      animal_has_chip: false
    request animal.album_file .pipe fs.create-write-stream opt.album + animal.album_file.match(/([^\/]+)$/).1
    div = $_.closest \div .next!find 'div:nth-child(odd)'
    for v, i in opt.fields => animal[v] = div.eq i .text! - /.*：/
    if animal.animal_id.match /^(\S+) \(.*:(\d+)\)/
      animal.animal_id = that.1
      animal.animal_has_chip = true
      animal.animal_chip_number = that.2
    animals.push animal
  return output animals if !img.length
  page index + 1, animals

# vi:et:nowrap
