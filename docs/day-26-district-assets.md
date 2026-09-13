# RescueTwin AI — Fictional District Asset Guide

## District identity

**Sundarpur District**, Bihar, India is a fictional river-and-canal district created for RescueTwin AI demonstrations.

The district vocabulary follows one shared naming system across the operational map, API payloads, decision engine, and incident reports.

## Zones

| ID | Public label |
| --- | --- |
| zone-01 | Riverbend |
| zone-02 | Old Wharf |
| zone-03 | Meadowgate |
| zone-04 | Eastbank |
| zone-05 | Civic Heights |
| zone-06 | Lakshmi Nagar |
| zone-07 | South Fields |
| zone-08 | Station Quarter |
| zone-09 | Greenridge |
| zone-10 | Canal View |

## Roads

Road labels use recognizable zone or landmark references and retain stable `road-XX` identifiers for routing.

Notable labels include **Civic Heights–Greenridge Arterial**, **Old Wharf–Lakshmi Bypass**, and **Riverbend–Canal Link**.

## Facilities

Hospitals:
- Civic Heights General Hospital
- Greenridge Community Hospital

Shelters:
- Meadowgate Secondary School
- Civic Heights Sports Hall
- Greenridge Community Center

## Rescue teams

- Delta Water Rescue
- Civic Medical Response
- Eastbank Search Unit
- South Fields Evacuation
- Greenridge Support Crew

## Asset rules

- IDs remain stable and machine-readable.
- Public labels remain human-readable.
- Every road endpoint references an existing zone.
- Every facility and rescue team references an existing zone.
- Facility occupancy cannot exceed capacity.
- District data remains static and deterministic.
