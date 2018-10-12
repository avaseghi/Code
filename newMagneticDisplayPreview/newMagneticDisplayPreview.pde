// Magnetic Display Preview for CaricaTron
// Drag to draw.
// Based on:
// The world pixel by pixel 2018
// Daniel Rozin

int cellSizeX= 12;                  // the X size of each pixel
int cellSizeY= 16;                  // the Y size of each pixel

void setup(){
 size(540, 840);
 background (0);
  for (int x = 0; x < width ; x+=cellSizeX){
     for (int y = 0; y < height ; y+=cellSizeY){
       fill(0);
       rect(x,y,cellSizeX,cellSizeY);
     }
  } 
}

void draw(){
  // do nothing
}

void mouseDragged(){
 int x=mouseX/cellSizeX;
 int y=mouseY/cellSizeY;
 
 x = x*cellSizeX;
 y = y*cellSizeY;
 
 fill(0);
 rect(x,y,cellSizeX,cellSizeY);
 fill(255);
 ellipse(x+cellSizeX/2,y+cellSizeY/2,cellSizeX*5.5/16,cellSizeY*5.5/16);
}
