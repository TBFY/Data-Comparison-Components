<p align="center"><img width=50% src="https://github.com/TBFY/general/blob/master/figures/tbfy-logo.png"></p>
<p align="center"><img width=40% src="https://github.com/TBFY/Data-Comparison-Components/blob/master/logo.png"></p>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[![Build Status](https://travis-ci.org/TBFY/harvester.svg?branch=master)](https://travis-ci.org/TBFY/Data-Comparison-Components)
[![Release Status](https://jitci.com/gh/TBFY/harvester/svg)](https://jitci.com/gh/TBFY/Data-Comparison-Components)
[![GitHub Issues](https://img.shields.io/github/issues/TBFY/harvester.svg)](https://github.com/TBFY/Data-Comparison-Components/issues)
[![License](https://img.shields.io/badge/license-Apache2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Info

This Repository is included in the works of [copin-compra-publica-inclusive](https://github.com/TBFY/copin-compra-publica-inclusive)

## Basic Overview

Download articles and legal documents from public procurement sources:
- Tender and contract data of European government bodies from [OpenOpps](https://openopps.com) via [API](http://theybuyforyou.eu/openopps-api/) or Amazon-S3 bucket (*credentials are required*)
- Legislative texts via [JRC-Acquis](https://ec.europa.eu/jrc/en/language-technologies/jrc-acquis) dataset.
- Public procurement notices via [TED](https://ted.europa.eu/) dataset.

And index them into [SOLR](http://lucene.apache.org/solr/) to perform complex queries and visualize results through [Banana](https://github.com/lucidworks/banana).

## Quick Start

1. Install [Docker](https://docs.docker.com/install/) and [Docker-Compose](https://docs.docker.com/compose/install/)
1. Clone this repo

	```
	git clone https://github.com/TBFY/Data-Comparison-Components.git
	```
1. Modify the `docker-compose.yml` file to adjust the filtering parameters
1. Run Siren.io by: `docker-compose up -d`
1. You should be able to monitor the progress by: `docker-compose logs -f`
1. A siren.io Admin site should be available at: [http://localhost:5606/](http://localhost:5606/)

## Environment 

Changing the `oid` reference
XXXX = 'ocdkls-dsnndfds53-tgg6yh'

## Contributing
Please take a look at our [contributing](https://github.com/TBFY/general/blob/master/guides/how-to-contribute.md) guidelines if you're interested in helping!
