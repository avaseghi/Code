
PImage img;
PImage rect;
int thresh = 5;

import oscP5.*;
import netP5.*;

int mouseXPrev =-1;
int mouseYPrev=-1;

OscP5 oscP5;
NetAddress myRemoteLocation;

int DOWN = 0;
int UP = 1;

int penPos = UP;
int cleanSlate = 0;
int header = 1;

void setup() {
  fullScreen();
  //size(1000,1000);
  background(0);
  img = loadImage("black.png");
  img.resize(950, 0);
  oscP5 = new OscP5(this, 5005); //listen for messages on 5005
  myRemoteLocation = new NetAddress("127.0.0.1", 5006); // Send messages to 5006
}

void draw() {
  if (penPos == DOWN) // penDown
  {
    print("me draw");
    img.loadPixels();
    loadPixels();
    //PxPSetPixel(mouseX, mouseY, 255, 255, 255, 255, pixels, width);
    int x= mouseX-100;
    int y= mouseY-150;
    print(x);
    print(",");
    println(y);
    if (x < img.width-thresh && y < img.height-thresh && x > thresh && y > thresh) {
      for (int i=-thresh; i<thresh; i++) {
        for (int j=-thresh; j<thresh; j++) {
          if(sqrt(i*i+j*j) <= thresh){
            PxPGetPixel(x+i, y+j, img.pixels, img.width);
            PxPSetPixel(x+100+i, y+150+j, 255, 255, 255, A, pixels, width);
          }
        }
      }
    }
    updatePixels();
  }
  if (cleanSlate ==1) {
    println("Cleaning slate");
    cleanSlateProtocol();
  }
  if(header ==1){
    println("heading");
    headerProtocol();
  }
}

// our function for getting color components , it requires that you have global variables
// R,G,B   (not elegant but the simples way to go, see the example PxP methods in object for
// a more elegant solution
int R, G, B, A;          // you must have these global varables to use the PxPGetPixel()
void PxPGetPixel(int x, int y, int[] pixelArray, int pixelsWidth) {
  int thisPixel=pixelArray[x+y*pixelsWidth];     // getting the colors as an int from the pixels[]
  A = (thisPixel >> 24) & 0xFF;                  // we need to shift and mask to get each component alone
  R = (thisPixel >> 16) & 0xFF;                  // this is faster than calling red(), green() , blue()
  G = (thisPixel >> 8) & 0xFF;
  B = thisPixel & 0xFF;
}

void PxPSetPixel(int x, int y, int r, int g, int b, int a, int[] pixelArray, int pixelsWidth) {
  a =(a << 24);
  r = r << 16;                       // We are packing all 4 composents into one int
  g = g << 8;                        // so we need to shift them to their places
  color argb = a | r | g | b;        // binary "or" operation adds them all into one int
  pixelArray[x+y*pixelsWidth]= argb;    // finaly we set the int with te colors into the pixels[]
}

void oscEvent(OscMessage theOscMessage) {
  /* check if theOscMessage has the address pattern we are looking for. */

  if (theOscMessage.checkAddrPattern("/test/")==true) {
    /* check if the typetag is the right one. */
    if (theOscMessage.checkTypetag("i")) {
      /* parse theOscMessage and extract the values from the osc message arguments. */
      int value = theOscMessage.get(0).intValue();

      print("### received an osc message /test with typetag i.");

      println(" value: "+value);

      if (value == UP) {
        mouseXPrev = -1;
        mouseYPrev = -1;
        penPos = value;
      }
      if (value == DOWN) {
        penPos = value;
      }
      if (value == 3) {
        cleanSlate=1;
        header=0;
      }
      if (value == 9) {
        cleanSlate=1;
        header =0;
      }
      if(value == 8){
        header = 1;
      }
      return;
    }
    println("### received an osc message /test with typetag"+theOscMessage.typetag());
  }
  println("### received an osc message. with address pattern "+theOscMessage.addrPattern());
}

void cleanSlateProtocol() {
  println("Clearing slate");
  background(0);

  //loadPixels();

  //for (int i=0; i<width; i++) {
  //  for (int j=0; i<height; j++) {
  //    PxPSetPixel(i, j, 0, 0, 0, 255, pixels, width);
  //  }
  //}

  //updatePixels();

  penPos = UP;
  cleanSlate = 0;
  println("Slate cleared");
}

void headerProtocol(){
  PImage img2;
  img2 = loadImage("caricatron.png");
  image(img2, 0, 0);
  filter(INVERT);
  header=0;
  println("Now showing header");
}
