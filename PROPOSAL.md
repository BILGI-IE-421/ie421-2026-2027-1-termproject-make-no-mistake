# The Shrinking Ice: is the Arctic losing its summer?

**Team:** make-no-mistake · **Theme:** T5 Hot Planet

**Members:** Ada Güner Nohut (122203012) · Canberk Doğruoğlu (122202090) · Tümer Kaan Mutlu (122203046) · Yağız Efe (122203062)

## The problem
Arctic sea ice is both a sign and a driver of global warming: when the ice melts, the darker ocean underneath absorbs more sunlight then warms up even more and causes more ice to melt. Sea ice follows a cycle that repeats every year: it reaches its largest extent in March, shrinks to its smallest extent in September and satellites have recorded this cycle since late 1978. While most people simply say “the ice is shrinking” we want to find out how the yearly cycle itself is changing, and how closely the summer loss follows temperature and CO<sub>2</sub>.


## The data

| Dataset | Link | What is in it |
|---|---|---|
| NSIDC Sea Ice Index (G02135) | [nsidc.org/data/seaice_index](https://nsidc.org/data/seaice_index) | Daily Arctic sea-ice extent (million km²) from November 1978 to today |
| NASA GISTEMP v4 | [data.giss.nasa.gov/gistemp](https://data.giss.nasa.gov/gistemp/) | Monthly and seasonal temperature anomalies for the globe and the Northern Hemisphere since 1880 |
| NOAA Mauna Loa CO2 | [gml.noaa.gov/ccgg/trends/data.html](https://gml.noaa.gov/ccgg/trends/data.html) | Monthly mean atmospheric CO2 (ppm) since 1958 |

We turn the daily ice data into monthly and yearly values, and join all three sources on **year and month** for 1979 onwards. That is the period when all three overlap.

## Our questions

1. How many days per year has Arctic sea ice been below the 1980s September average, and when did that start to climb?
2. Is a warm Northern Hemisphere spring associated with a lower September ice minimum later that year?
3. Has September ice declined faster per 10 ppm of CO₂ since 2000 than before?
