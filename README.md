# beamspot_locator
  Produces a report with beamspots relative to cryostat position


## Usage

1. Update `settings.py` with the correct directory, reference image (for your sample position), and sample location
2. Update `images.csv` with filenames. 
  * Files must have the format `yymmdd_hhmmTyymmdd_hhmm_fieldT_biaskV`.fits`. Example: `210815_1111_T210813_0059_2p2T_15kV.fits`
  * First timestamp is image time. Second is tune ID.
3. Run `python3 main.py`
4. Check `beamspots.py` for results
