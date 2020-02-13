<p align="center"><img width=50% src="https://github.com/TBFY/general/blob/master/figures/tbfy-logo.png"></p>
<p align="center"><img width=40% src="https://github.com/TBFY/Data-Comparison-Components/blob/master/logo.png"></p>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[![GitHub Issues](https://img.shields.io/github/issues/TBFY/harvester.svg)](https://github.com/TBFY/Data-Comparison-Components/issues)
[![License](https://img.shields.io/badge/license-Apache2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Info

This Repository is included in the works of [copin-compra-publica-inclusive](https://github.com/TBFY/copin-compra-publica-inclusive)

## Basic Overview

Download articles and legal documents from public procurement sources:
- Tender and contract data of European government bodies from [OpenOpps](https://openopps.com) via [API](http://theybuyforyou.eu/openopps-api/) or Amazon-S3 bucket (*credentials are required*)
- Legislative texts via [JRC-Acquis](https://ec.europa.eu/jrc/en/language-technologies/jrc-acquis) dataset.
- Public procurement notices via [TED](https://ted.europa.eu/) dataset.

## Quick Start

1. Install [Docker](https://docs.docker.com/install/) and [Docker-Compose](https://docs.docker.com/compose/install/)
1. Software and Hardware requirements for the Docker platform
1. Clone this repo
	```
	git clone https://github.com/TBFY/Data-Comparison-Components.git
	```
1. Modify the `docker-compose.yml` file to adjust the filtering parameters
- IDTENDER_SEARCH: id in search-api for similar tender
- TOTAL_DATOS_TENDER_SEARCH: Maximum number of records to retrieve from search-api
- TOTAL_DATOS_TENDER: Maximum data to recover from kg-api for Tender
- TOTAL_DATOS_AWARD: Maximum data to recover from kg-api for Award
- TOTAL_DATOS_CONTRACTING_PROCESS: Maximum data to recover from kg-api for Contracting Process
1. Run the container Docker by: `docker-compose up -d`
1. You should be able to monitor the progress by: `docker-compose logs -f`
1. Run de exec `docker-compose exec -T siren sh init.sh` to launch the data upload
1. For admin site should be available at: [http://localhost:5606/](http://localhost:5606/)

## Docker Requirements

It is necessary that the Docker machine meets the following requirements:
https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#_set_vm_max_map_count_to_at_least_262144
- Modify /etc/sysctl.conf to add, according to the documentation of [ElasticSearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#_set_vm_max_map_count_to_at_least_262144)
	```
	vm.max_map_count=262144
	```

## Contributing
Please take a look at our [contributing](https://github.com/TBFY/general/blob/master/guides/how-to-contribute.md) guidelines if you're interested in helping!
