
# XBLOCK

Create your xblocks here and test them out with the xblock-sdk

Follow instructions of xblock sdk and xblock creation:

<https://docs.openedx.org/projects/xblock/en/latest/xblock-tutorial/getting_started/prereqs.html>

->xblock-env/Scripts/activate
->(xblock-env)  pip install -e ibal_chat_xblock
->(xblock-env)  python xblock-sdk/manage.py migrate
->(xblock-env)  python xblock-sdk/manage.py runserver --noreload

Run Tutor local start - dont use launch coz it erases container

First run use two terminals
docker exec -u root -it tutor_local-cms-1 bash

docker cp "C:\Coding Projects\ibal-project\xblock_development\testxbloc" tutor_local-cms-1:/openedx/testxbloc

cd /openedx/testxbloc && pip install -e .

docker exec -u root -it tutor_local-lms-1 bash

docker cp "C:\Coding Projects\ibal-project\xblock_development\testxbloc" tutor_local-lms-1:/openedx/testxbloc

cd /openedx/testxbloc && pip install -e .

tutor local stop and then start.
Add it in Studio.local -> Advanced Settings ->["xbloc1","xbloc2"]

Then run below command in docker execute

cd /openedx/shinblock && pip install -e .
