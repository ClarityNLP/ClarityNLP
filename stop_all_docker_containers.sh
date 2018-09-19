#/bin/bash

echo "Killing all these containers (Ctri+C to cancel)..."
docker ps 
for i in {15..1};do echo  "Killing in $i seconds." && sleep 1; done

docker kill $(docker ps -q)

echo "Done."
