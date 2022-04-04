Tests go from simple to complicated.
Features to test include:
- r/w locally (csv, postgres)
- r/w remote (gcp, aws, etc)
- pass to graph 
    - blockstack contract
    - ETL process
- runtime config
    - parametrically generate config.yml files
- query the graph? 


Data Access Object (DAO)

Currently the DataIO Context supplies strategies, could those strategies 
 - be shared as a DAO?
 - be given new methods?