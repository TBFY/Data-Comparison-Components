<p align="center"><img width=50% src="https://github.com/TBFY/general/blob/master/figures/tbfy-logo.png"></p>
<p align="center"><img width=40% src="https://github.com/TBFY/Data-Comparison-Components/blob/master/logo.png"></p>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[![GitHub Issues](https://img.shields.io/github/issues/TBFY/harvester.svg)](https://github.com/TBFY/Data-Comparison-Components/issues)
[![License](https://img.shields.io/badge/license-Apache2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Info

This repository contains the development done by Oesía for Task “2.5 Data comparison components”

Download articles and legal documents from public procurement sources:
- Tender and contract data of European government bodies from [OpenOpps](https://openopps.com) via [API](http://theybuyforyou.eu/openopps-api/) or Amazon-S3 bucket (*credentials are required*)
- Legislative texts via [JRC-Acquis](https://ec.europa.eu/jrc/en/language-technologies/jrc-acquis) dataset.
- Public procurement notices via [TED](https://ted.europa.eu/) dataset.

## Basic Overview

The tool is used to analyze the information extracted from the KG through the 2 project APIs designed to work with the Knowledge Graph: [KG core api](https://github.com/TBFY/knowledge-graph-API) and [search api](https://github.com/TBFY/search-API).

The core API basically brings bidding information while the Api search searches, from an OCID, for documents containing similar descriptions ("description" field) regardless of the language.

This comparison tool analyses the bidding and award data that is extracted from an initial load. To perform this initial load, you must indicate the number of tenders and awards that you want to search for the KG. And, to use the api search, you are asked for the ID of the document you want to compare. All this parameterization is done together at the beginning.

## Quick Start

1. Install [Docker](https://docs.docker.com/install/) and [Docker-Compose](https://docs.docker.com/compose/install/)
1. Software and Hardware requirements for the Docker platform
1. Clone this repo
	```
	git clone https://github.com/TBFY/Data-Comparison-Components.git
	```
1. Modify the `docker-compose.yml` file to adjust the volume of data to be extracted from the KG-API and the search-API on initial tool loading
- IDTENDER_SEARCH: id in search-api for similar tender
- TOTAL_DATOS_TENDER_SEARCH: Maximum number of records to retrieve from search-api
- TOTAL_DATOS_TENDER: Maximum data to recover from kg-api for Tender
- STATUS_DATOS_TENDER: Status of the tender (planning, planned, active, canceled, unsuccessful, complete, withdrawn), if left on the side, the filter is not applied
- TITLE_DATOS_TENDER: A word to filter, if left empty the filter is not applied
- DESCRIPTION_DATOS_TENDER: A word to filter, if left empty the filter is not applied
- TOTAL_DATOS_AWARD: Maximum data to recover from kg-api for Award
- STATUS_DATOS_AWARD: Status of the award (pending, active, canceled, unsuccessful), if left on the side, the filter is not applied
- TITLE_DATOS_AWARD: A word to filter, if left empty the filter is not applied
- DESCRIPTION_DATOS_AWARD: A word to filter, if left empty the filter is not applied
- TOTAL_DATOS_CONTRACTING_PROCESS: Maximum data to recover from kg-api for Contracting Process
1. Run the container Docker by: `docker-compose up -d`
1. You should be able to monitor the progress by: `docker-compose logs -f`
1. Run de exec `docker-compose exec -T siren sh init.sh` to launch the data upload
In the final result of the data loading there will be more data than the limits indicated, this is due to the fact that the related Tenders and Awards are also loaded.
1. For admin site should be available at: [http://localhost:5606/](http://localhost:5606/)
- User: sirenadmin
- Password: password
## Docker Requirements

It is necessary that the Docker machine meets the following requirements:
https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#_set_vm_max_map_count_to_at_least_262144
- Modify /etc/sysctl.conf to add, according to the documentation of [ElasticSearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#_set_vm_max_map_count_to_at_least_262144)
	```
	vm.max_map_count=262144
	```
## Lastest Stable Release
Lastest stable release can be found here:

https://hub.docker.com/repository/docker/tbfy/odc-tool

## Contributing
Please take a look at our [contributing](https://github.com/TBFY/general/blob/master/guides/how-to-contribute.md) guidelines if you're interested in helping!
