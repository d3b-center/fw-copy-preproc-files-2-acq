# SDK gear to rename and copy pre-processed files

This gear takes the output of d3b-ped-preproc-pipeline-batch, renames the files (images and segmentations) to start with "CID_age_" and copies them to a "processed" acquisition directory in the same session.

## Usage

Run at the session-level.

### Inputs

None

### Configuration

* __debug__ (boolean, default False): Include debug statements in output.

### Limitations

Current limitations of the gear are as follows:

* 

