FROM node:15.11.0-buster

RUN mkdir /home/node/app
WORKDIR /home/node/app

COPY rollup.config.js .
COPY package*.json .

#RUN npm config set unsafe-perm true
RUN npm install

COPY ./src ./src
COPY ./public ./public

RUN npm run-script build

EXPOSE 5000

ENV HOST=0.0.0.0

COPY src .

RUN chown node -R .

USER node
CMD ["npm", "run", "dev"]
