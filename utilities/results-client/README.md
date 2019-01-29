## results-viewer


### To run standalone
1. Copy `.env.example` to `.env`, and edit with your properties.
2. Making sure `npm` is installed, run
```javascript
npm install
```
and 
```javascript
npm start
```
3. The application runs by default [here](http://localhost:8200).

### Running Docker standalone
1. Build image
```
docker build -t results-viewer-app .
```
2. Run the image
```
docker run -it -v ${PWD}:/usr/src/app -v /usr/src/app/node_modules -p 8200:8200 --rm results-viewer-app
```
3. The application runs by default [here](http://localhost:8200).
