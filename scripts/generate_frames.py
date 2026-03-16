#!/usr/bin/env python3
"""
Generate bold ASCII animation frames for the Franc homepage.
Ghostty-inspired: dense filled silhouettes with character shading.

Character density hierarchy (heaviest to lightest):
  @ # $ % * + = - . : (space)
"""

import json
import random
import math
import os

random.seed(42)

WIDTH = 78
HEIGHT = 40

# ============================================================
# BOLD SHIP — Dense filled galleon
# Sails: solid $$%% fill with shading gradient
# Hull: heavy @@##$$ fill
# Water: animated ~-=.
# ============================================================
SHIP_RAW = r"""
                                                                              
         .              *                    .              *                 
      *          .             .                   .             .       *    
                        .             *                       .              
                                                                              
                                    $                                         
                                   $%$                                        
                                  $%*%$                                       
                                 $%*+|*%$                                     
                                $%*+.|.+*%$                                   
                               $%*+..|..+*%$                                  
                              $%*+...|...+*%$                                 
                             $%*+....|....+*%$                                
                            $%*+.....|.....+*%$                               
                           $%*+......|......+*%$                              
                          $%*+.......|.......+*%$                             
                         $%*+........|........+*%$                            
                        @@@@@@@@@@@@@@@@@@@@@@@@@@@                           
                       @@@#####$$$$$$$$$$$$$#####@@@                          
                      @@@##$$$$$$$$$$$$$$$$$$$$##@@@                          
                     @@@#$$. . . F R A N C . . .$#@@@                        
                    @@@##$$$$$$$$$$$$$$$$$$$$$$$$$#@@@@                       
                   @@@@##$$$$$$$$$$$$$$$$$$$$$$$$$##@@@@                      
                  @@@@@#####$$$$$$$$$$$$$$$$$#######@@@@@                     
                   @@@@#####$$$$$$$$$$$$$$$$$######@@@@@                      
                    @@@########$$$$$$$$$$$########@@@                         
             ~~.~.~~~.~.@@@@#####$$$$$$$#####@@@@~.~~.~.~.~~                  
          ~.~.~-~.~.~.~-~.~.~==@@@#####@@@==~.~-~.~.~-~.~.~-~.~              
        ~.~.~-~.~.~.~-~.~.~-~.~.~-~.~-~.~.~-~.~.~.~-~.~.~-~.~.~~           
       ~.~.~-~.~.~.~-~.~.~-~.~.~-~.~-~.~.~-~.~.~.~-~.~.~-~.~.~-~.          
      ~.~.~-~.~.~.~-~.~.~-~.~.~-~.~-~.~.~-~.~.~.~-~.~.~-~.~.~-~.~.~        
     ~.~.~-~.~.~.~-~.~.~-~.~.~-~.~-~.~.~-~.~.~.~-~.~.~-~.~.~-~.~.~-~.      
                                                                              
      |  multi pertransibunt et augebitur scientia                      |    
                                                                              
                                                                              
                                                                              
                                                                              
                                                                              
""".strip('\n').split('\n')


ROCKET_RAW = r"""
                                                                              
         *              .                    *              .                 
      .          *             *                   *             *       .    
                        *             .                       *              
                                                                              
                                   .#.                                        
                                  .#$#.                                       
                                 .#$%$#.                                      
                                .#$%.%$#.                                     
                               .#$%.*.$%#.                                    
                              .#$%. * .$%#.                                   
                              |#$. ( ) .$#|                                   
                              |#$. $$$ .$#|                                   
                              |#$. FRN .$#|                                   
                              |#$. $$$ .$#|                                   
                              |#$.     .$#|                                   
                              |#$.     .$#|                                   
                              |#$_______$#|                                   
                             @@#$$$$$$$$$#@@                                  
                            @@@#$$$$$$$$$#@@@                                 
                           @@@##$$$$$$$$$##@@@                                
                          @@@#$. FRANC .$#@@@@                                
                         @@@##$_________$##@@@@                               
                        @@@##$$/       \$$##@@@                               
                       @@@@#$$/   . .   \$$#@@@@                              
                        @@@#$$$$$$$$$$$$$$$#@@@                               
                         @@@@#$$$$$$$$$$$#@@@@                                
                           .^^.^^^^^^^^.^^.                                   
                         .^^^^^.^^^^^^.^^^^^.                                 
                        ^^^^^^^^^.^^.^^^^^^^^^                                
                       ^^^^^^^^^^^^.^^^^^^^^^^^^                              
                      ^^^^^^^^^^^^^^^^^.^^^^^^^^^                             
                                                                              
      |  ad astra per curiositatem                                      |    
                                                                              
                                                                              
                                                                              
                                                                              
                                                                              
""".strip('\n').split('\n')


def pad_lines(raw, width=WIDTH, height=HEIGHT):
    result = []
    for line in raw[:height]:
        if len(line) < width:
            line += ' ' * (width - len(line))
        elif len(line) > width:
            line = line[:width]
        result.append(line)
    while len(result) < height:
        result.append(' ' * width)
    return result


def make_stars(width=WIDTH, height=5, density=0.005, seed=42):
    rng = random.Random(seed)
    return [(x, y) for y in range(height) for x in range(width) if rng.random() < density]

STARS = make_stars()


def twinkle(lines, f):
    r = [list(l) for l in lines]
    chars = '..*+. *.'
    for x, y in STARS:
        if y < len(r) and x < len(r[y]) and r[y][x] == ' ':
            phase = (f * 3 + x * 7 + y * 13) % 12
            if phase < 5:
                r[y][x] = chars[phase % len(chars)]
    return [''.join(row) for row in r]


def animate_waves(lines, f):
    result = list(lines)
    wave = '~.~-~.~='
    for i, line in enumerate(lines):
        if '~' not in line:
            continue
        cs = list(line)
        j = 0
        while j < len(cs):
            if cs[j] in '~-.=':
                start = j
                while j < len(cs) and cs[j] in '~-.=':
                    j += 1
                end = j
                if end - start > 3:
                    off = (f * 2 + i * 3) % len(wave)
                    for k in range(start, end):
                        cs[k] = wave[(k + off) % len(wave)]
            else:
                j += 1
        result[i] = ''.join(cs)
    return result


def animate_exhaust(lines, f):
    result = list(lines)
    flames = ['^*o.^*o.', '*o.^^*o.', 'o.^*^o.*', '.^*o.*^o']
    fset = flames[f % len(flames)]
    for i, line in enumerate(lines):
        if '^' not in line:
            continue
        cs = list(line)
        for j, c in enumerate(cs):
            if c == '^':
                cs[j] = fset[(j * 3 + i * 5 + f * 7) % len(fset)]
        result[i] = ''.join(cs)
    return result


def gen_ship(n=36):
    base = pad_lines(SHIP_RAW)
    return [twinkle(animate_waves(base, f), f) for f in range(n)]


def gen_rocket(n=36):
    base = pad_lines(ROCKET_RAW)
    return [twinkle(animate_exhaust(base, f), f + 81) for f in range(n)]


def gen_morph(n=48):
    ship = pad_lines(SHIP_RAW)
    rocket = pad_lines(ROCKET_RAW)
    scramble = '@#$%&*ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+~=.'
    cx, cy = WIDTH // 2, HEIGHT // 2
    md = math.sqrt(cx**2 + cy**2)
    rng = random.Random(123)
    reveal = [[(math.sqrt((x-cx)**2+((y-cy)*2)**2)/md*0.5 + rng.random()*0.5) for x in range(WIDTH)] for y in range(HEIGHT)]

    frames = []
    for f in range(n):
        p = f / (n - 1)
        lines = []
        for y in range(HEIGHT):
            row = []
            for x in range(WIDTH):
                s = ship[y][x] if y < len(ship) and x < len(ship[y]) else ' '
                r = rocket[y][x] if y < len(rocket) and x < len(rocket[y]) else ' '
                t = reveal[y][x]
                if p < t * 0.6:
                    row.append(s)
                elif p > t * 0.6 + 0.3:
                    row.append(r)
                elif s == ' ' and r == ' ':
                    row.append(' ')
                elif rng.random() < 0.5:
                    row.append(rng.choice(scramble))
                else:
                    row.append(r if p > 0.5 else s)
            lines.append(''.join(row))
        frames.append(twinkle(lines, f + 36))
    return frames


def main():
    print('Generating...')
    ship = gen_ship(36)
    morph = gen_morph(48)
    rocket = gen_rocket(36)

    data = {
        'ship': ship, 'morph': morph, 'rocket': rocket,
        'meta': {'width': WIDTH, 'height': HEIGHT, 'fps': 8,
                 'ship_count': len(ship), 'morph_count': len(morph), 'rocket_count': len(rocket)}
    }

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'frames.json')
    with open(out, 'w') as f:
        json.dump(data, f, separators=(',', ':'))

    kb = os.path.getsize(out) / 1024
    total = len(ship) + len(morph) + len(rocket)
    print(f'{total} frames, {kb:.1f} KB')

    print('\n=== SHIP 0 ===')
    for l in ship[0]: print(l)
    print('\n=== ROCKET 0 ===')
    for l in rocket[0]: print(l)


if __name__ == '__main__':
    main()
