



# Requirements

## nautobot

nautobot is the default SOT we use. 

## github/gitlab
To store defaults and other mandatory settings you need a git.
An example structure looks like:

sot_data (or name it like you want it)<br>
* config_context (used by nautobot)
* config_context_schemas (used by nautobot)
* templates
* config_backups
* defaults (used by the abstraction layer and our miniapps)
  - prefixe.yaml 
  - basedata.yaml
  - lldm.yaml
