# Data o klimatu
The data as prepared by the beatiful [faktaoklimatu](https://faktaoklimatu.cz/) project and website, processed in python to produce similar charts, slightly interactive (with plotly). 

Check the results online at [data-o-klimatu](https://data-o-klimatu.netlify.app/).

## how this is setup
- jupyter lab
- jupytext with synchronization, git lfs for both ipynb (is it really needed though ?)  and html files
- a small static website where the reports could be published from lfs

## todo
### jlab
- prepare a notebook skeleton
 - along with a "rules" document
 - describe process (with both editor & jlab env & console to the right)
- code formatting
- toc, especially for the exported - https://jupyter-contrib-nbextensions.readthedocs.io/en/latest/nbextensions/toc2/README.html
- docker to make it easier for ppl

- instructions for installing
- writeup about usage


## to do for publishing
- favicon
- google
- domain ?
- og image ?
- footer
- about page
- link to github for notebook
- some kind of styling ?

## publishing notebooks
jupyter nbconvert --template=basic --to=html --output-dir=work  notebooks/tropic_days.ipynb
python -m pynetlify deploy_folder --site-id 92182069-95ba-4331-8a96-2e953050a314 public

## random thoughts
currently plotly doesnt work with new jlab, has to be installed locally - https://github.com/plotly/plotly.py/issues/2994

also jedi has to be uninstalled for code completion to work (uninstall didnt help, still have to do the below)
%config Completer.use_jedi = False

plotly lib is not always included ... for such cases we tell require.js to fetch it from a CDN
https://cdnjs.cloudflare.com/ajax/libs/plotly.js/1.58.2/plotly.min.js
obviously, the best would be to solve it in jupyter :)


## ideas
- warming chart - make a comparison about how much co2 the nations produce vs how warm it gets vs how wealthy they are
- try adding links to nice articles about effects of warming (ie siberia natgeo)
- amount of ppl in warm areas ? -> refugees ...
- warming - 2020 ? looks like it got much worse ...

## todo
- plotly & geojson polygons 
  - question asked https://community.plotly.com/t/geojson-data-in-scatter-geo-only-draws-points-not-areas/48804
- publishing on deepnote (currently not very plotly friendly) - ask