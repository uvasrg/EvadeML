a = Dir.entries(".")
hash = Hash.new
a.each{|d|
	if (d == "." || d == ".." || !File.directory?(d)) then next end
	b = Dir.entries(d)
	added = false
	b.each{|d2|
		if (d2 == "." || d2 == "..") then next end
		if (d2 == "generic.txt")
			added = true
			if (hash.has_key? "doubleclick.net.txt") then hash["doubleclick.net.txt"] += 1 else hash["doubleclick.net.txt"] = 1 end
			if (hash.has_key? "googleadservices.com.txt") then hash["googleadservices.com.txt"] += 1 else hash["googleadservices.com.txt"] = 1 end
		end
		if (hash.has_key? d2) then hash[d2]+=1 else hash[d2] = 1 end
		if ((d2 == "doubleclick.net.txt" || d2 == "googleadservices.com.txt") && added) then hash[d2]-=1 end
	}
}
p hash